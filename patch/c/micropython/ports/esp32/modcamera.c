// Code adapted from https://github.com/espressif/esp32-camera
#include "string.h"
#include "esp_camera.h"
#include "esp_log.h"
#include "esp_jpg_decode.h"

#include "py/nlr.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"

#define TAG "camera"

//WROVER-KIT PIN Map
#define CAM_PIN_PWDN    32 //power down is not used
#define CAM_PIN_RESET   -1 //software reset will be performed
#define CAM_PIN_XCLK     0
#define CAM_PIN_SIOD    26 // SDA
#define CAM_PIN_SIOC    27 // SCL

#define CAM_PIN_D7      35
#define CAM_PIN_D6      34
#define CAM_PIN_D5      39
#define CAM_PIN_D4      36
#define CAM_PIN_D3      21
#define CAM_PIN_D2      19
#define CAM_PIN_D1      18
#define CAM_PIN_D0       5
#define CAM_PIN_VSYNC   25
#define CAM_PIN_HREF    23
#define CAM_PIN_PCLK    22

#define min(a,b) ((a)<(b) ?(a):(b))
#define max(a,b) ((a)>(b) ?(a):(b))
static camera_config_t camera_config = {
	.pin_pwdn  = CAM_PIN_PWDN,
	.pin_reset = CAM_PIN_RESET,
	.pin_xclk = CAM_PIN_XCLK,
	.pin_sscb_sda = CAM_PIN_SIOD,
	.pin_sscb_scl = CAM_PIN_SIOC,

	.pin_d7 = CAM_PIN_D7,
	.pin_d6 = CAM_PIN_D6,
	.pin_d5 = CAM_PIN_D5,
	.pin_d4 = CAM_PIN_D4,
	.pin_d3 = CAM_PIN_D3,
	.pin_d2 = CAM_PIN_D2,
	.pin_d1 = CAM_PIN_D1,
	.pin_d0 = CAM_PIN_D0,
	.pin_vsync = CAM_PIN_VSYNC,
	.pin_href = CAM_PIN_HREF,
	.pin_pclk = CAM_PIN_PCLK,

	//XCLK 20MHz or 10MHz for OV2640 double FPS (Experimental)
	.xclk_freq_hz = 20000000,
	.ledc_timer = LEDC_TIMER_0,
	.ledc_channel = LEDC_CHANNEL_0,

	.pixel_format = PIXFORMAT_JPEG,//YUV422,GRAYSCALE,RGB565,JPEG
	.frame_size = FRAMESIZE_UXGA,//QQVGA-UXGA Do not use sizes above QVGA when not JPEG

	.jpeg_quality = 12, //0-63 lower number means higher quality
	.fb_count = 1 //if more than one, i2s runs in continuous mode. Use only with JPEG
};

#include "esp_system.h"
#include "esp_spi_flash.h"


STATIC mp_obj_t camera_init(){
	esp_err_t err = esp_camera_init(&camera_config);
	if (err != ESP_OK) {
		ESP_LOGE(TAG, "Camera init failed");
		return mp_const_false;
	}

	return mp_const_true;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_init_obj, camera_init);


STATIC mp_obj_t camera_deinit(){
	esp_err_t err = esp_camera_deinit();
	if (err != ESP_OK) {
		ESP_LOGE(TAG, "Camera deinit failed");
		return mp_const_false;
	}

	return mp_const_true;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_deinit_obj, camera_deinit);


STATIC mp_obj_t camera_capture(){
	//acquire a frame
	camera_fb_t * fb = esp_camera_fb_get();
	if (!fb) {
		ESP_LOGE(TAG, "Camera capture Failed");
		return mp_const_false;
	}

	mp_obj_t image = mp_obj_new_bytes(fb->buf, fb->len);

	//return the frame buffer back to the driver for reuse
	esp_camera_fb_return(fb);
	return image;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_capture_obj, camera_capture);

#define SQUARE_DETECTION 8
typedef struct 
{
	uint16_t       height;
	uint16_t       width;
	const uint8_t *input;
	uint16_t       max;
	uint16_t       access;
	uint16_t       *reds;
	uint16_t       *greens;
	uint16_t       *blues;

	uint16_t       *hues;
	uint16_t       *saturations;
	uint16_t       *lights;

	uint8_t        *motion;
} camera_motion_detect_t;


static void *_malloc(size_t size)
{
	return heap_caps_calloc(1, size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
}

/** Conversion from HSL to RGB color
@param hue hue value (0-359)
@param saturation saturation value (0-100)
@param light light value (0-100) */
void camera_hsl_to_rgb(uint32_t hue, uint32_t saturation, uint32_t light, uint32_t *red, uint32_t *green, uint32_t *blue)
{
	int v;
	int m, sv, fract, vsf, mid1, mid2, sextant;
	*red = *green = *blue = 0;

	hue %= 360;
	v = (light < 50) ? (light * (saturation + 100) / 100) : (light + saturation - (light * saturation / 100));
	if (v > 0) 
	{
		m = light + light - v;
		sv = 100 * (v - m) / v;

		sextant = hue/60;
		fract = 100 * (hue - (sextant * 60)) / 60;
		vsf = v * sv * fract / 10000;
		mid1 = m + vsf;
		mid2 = v - vsf;

		switch (sextant) 
		{
		case 0: 
			*red = v;
			*green = mid1;
			*blue = m;
			break;

		case 1:
			*red = mid2;
			*green = v;
			*blue = m;
			break;

		case 2:
			*red = m;
			*green = v;
			*blue = mid1;
			break;

		case 3:
			*red = m;
			*green = mid2;
			*blue = v;
			break;

		case 4:
			*red = mid1;
			*green = m;
			*blue = v;
			break;

		case 5:
			*red = v;
			*green = m;
			*blue = mid2;
			break;
		}

		*red   = (*red   * 255) / 100;
		*green = (*green * 255) / 100;
		*blue  = (*blue  * 255) / 100;
	}
}




/** Conversion from RGB to HSL color space. 
@param color color to convert
@param hue hue value returned (0-359)
@param saturation saturation value returned (0-100)
@param light light value returned (0-100) */
void camera_rgb_to_hsl(uint32_t red, uint32_t green, uint32_t blue, uint32_t *hue, uint32_t *saturation, uint32_t *light)
{
	uint32_t v, m, vm;
	uint32_t hue2, saturation2, light2;

	if (hue && saturation && light)
	{
		red   = red   << 8;
		green = green << 8;
		blue  = blue  << 8;
		
		hue2 = saturation2 = light2 = 0;

		v = max(red,green);
		v = max(v,blue);
		m = min(red,green);
		m = min(m,blue);

		light2 = (m + v)/2;
		if (light2 != 0) 
		{
			saturation2 = vm = (v - m);
			if (saturation2 != 0)
			{
				uint32_t red2, green2, blue2;
				saturation2 = (saturation2 << 16) / ((light2 < 32768) ? (v+m) : (131072 - v - m));

				red2   = ((((v-red)   << 16) / vm) * 60) >> 16;
				green2 = ((((v-green) << 16) / vm) * 60) >> 16;
				blue2  = ((((v-blue)  << 16) / vm) * 60) >> 16;

				if (red == v)
				{
					hue2 = (green == m ? 300 + blue2 : 60 - green2);
				}
				else if (green == v)
				{
					hue2 = (blue == m ? 60 + red2 : 180 - blue2);
				}
				else
				{
					hue2 = (red == m ? 180 + green2 : 300 - red2);
				}
			}
		}

		*hue = hue2 % 360;
		*saturation = (saturation2 * 100) >> 16;
		*light = (light2 * 100) >> 16;
	}
}


// input buffer
static uint32_t camera_jpg_read(void * arg, size_t index, uint8_t *buf, size_t len)
{
	camera_motion_detect_t * motion = (camera_motion_detect_t *)arg;
	if(buf) 
	{
		memcpy(buf, motion->input + index, len);
	}
	return len;
}

//output buffer and image width
static bool camera_get_motion_matrix(void * arg, uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint8_t *data)
{
	camera_motion_detect_t * motion = (camera_motion_detect_t *)arg;
	
	// First access
	if(!data)
	{
		if(x == 0 && y == 0)
		{
			// Get the size of image
			motion->width  = w;
			motion->height = h;
			motion->max    = ((w/SQUARE_DETECTION) + (w % SQUARE_DETECTION == 0 ? 0 : 1)) * ((h/SQUARE_DETECTION) + (h % SQUARE_DETECTION == 0 ? 0 : 1));
			//~ ESP_LOGE(TAG, "motion %dx%d",w,h);
			motion->reds        = (uint16_t*)_malloc(sizeof(uint16_t) * motion->max);
			motion->greens      = (uint16_t*)_malloc(sizeof(uint16_t) * motion->max);
			motion->blues       = (uint16_t*)_malloc(sizeof(uint16_t) * motion->max);
			motion->hues        = (uint16_t*)_malloc(sizeof(uint16_t) * motion->max);
			motion->saturations = (uint16_t*)_malloc(sizeof(uint16_t) * motion->max);
			motion->lights      = (uint16_t*)_malloc(sizeof(uint16_t) * motion->max);
		}
		else
		{
			// Write end
		}
	}
	else
	{
		uint16_t *reds;
		uint16_t *greens;
		uint16_t *blues;
		uint16_t Y, X;
		
		//~ ESP_LOGE(TAG, "motion x=%d y=%d w=%d h=%d %dx%d (%d) %02X%02X%02X %02X%02X%02X",x,y,w,h, motion->width, motion->height, motion->access++,data[0],data[1],data[2],data[3],data[4],data[5]);

		// Compute the motion in the square detection
		for (Y = y; Y < (y + h); Y ++)
		{
			reds   = motion->reds;
			greens = motion->greens;
			blues  = motion->blues;
			
			for (X = x; X < (x + w); X ++) 
			{
				uint16_t posX = ((Y/SQUARE_DETECTION)*(motion->width/SQUARE_DETECTION)) + X / SQUARE_DETECTION;
				reds  [posX] += data[(X-x)*3+2]; // Red
				greens[posX] += data[(X-x)*3+1]; // Green
				blues [posX] += data[(X-x)*3];   // Blue
				//~ ESP_LOGE(TAG, "%d:%d %d %d", posX, reds[posX], greens[posX], blues[posX]);
			}
			data += (w * 3);
		}
	}
	
	/*
import camera
camera.init()
camera.framesize(camera.FRAMESIZE_QQVGA)
camera.pixformat(camera.PIXFORMAT_JPEG)


import camera
camera.init()
camera.framesize(camera.FRAMESIZE_UXGA)
camera.pixformat(camera.PIXFORMAT_JPEG)

import machine
import uos
uos.mount(machine.SDCard(), "/sd")
i = 1
def snap():

global i
image, reds, greens, blues = camera.motion()
file = open("/sd/%d_img.jpg"%i,"wb")
file.write(image)
file.close()
file = open("/sd/%d_reds.bin"%i,"wb")
file.write(reds)
file.close()
file = open("/sd/%d_greens.bin"%i,"wb")
file.write(greens)
file.close()
file = open("/sd/%d_blues.bin"%i,"wb")
file.write(blues)
file.close()
i += 1


for j in range(20): print(i);snap()


uos.umount("/sd")

	*/
	return true;
}


STATIC mp_obj_t camera_motion_detection()
{
	// Acquire a frame
	camera_fb_t * fb = esp_camera_fb_get();
	if (!fb) 
	{
		ESP_LOGE(TAG, "Camera capture Failed");
		return mp_const_false;
	}
	mp_obj_t image = mp_obj_new_bytes(fb->buf, fb->len);

	//return the frame buffer back to the driver for reuse
	esp_camera_fb_return(fb);
	
	// Add image in returned list
	mp_obj_t res = mp_obj_new_list(0, NULL);
	mp_obj_list_append(res, image);

	camera_motion_detect_t motionDetector;
	memset(&motionDetector, 0, sizeof(motionDetector));
	motionDetector.input = fb->buf;
	
	// Compute motion detection
	esp_err_t ret = esp_jpg_decode(fb->len, JPG_SCALE_8X, camera_jpg_read, camera_get_motion_matrix, (void*)&motionDetector);

	if (ret == ESP_OK)
	{
		int i;
		uint8_t * pBluesRes     = (uint8_t*)motionDetector.blues;
		uint8_t * pRedRes       = (uint8_t*)motionDetector.reds;
		uint8_t * pGreenRes     = (uint8_t*)motionDetector.greens;
		uint16_t * pHues        = motionDetector.hues;
		uint16_t * pSaturations = motionDetector.saturations;
		uint16_t * pLights      = motionDetector.lights;
		uint32_t red;
		uint32_t green;
		uint32_t blue;
		uint32_t hue;
		uint32_t saturation;
		uint32_t light;
		
		for (i = 0; i < motionDetector.max; i++)
		{
			// Calculate the average on the detection square
			motionDetector.blues [i] = motionDetector.blues [i]/SQUARE_DETECTION/SQUARE_DETECTION;
			motionDetector.reds  [i] = motionDetector.reds  [i]/SQUARE_DETECTION/SQUARE_DETECTION;
			motionDetector.greens[i] = motionDetector.greens[i]/SQUARE_DETECTION/SQUARE_DETECTION;
			
			blue  = (uint8_t)motionDetector.blues  [i];
			red   = (uint8_t)motionDetector.reds   [i];
			green = (uint8_t)motionDetector.greens [i];
			
			// Reduces the size of data to be returned
			*pBluesRes = blue;
			*pRedRes   = red;
			*pGreenRes = green;
			
			camera_rgb_to_hsl(red, green, blue, &hue, &saturation, &light);

			*pHues        = (uint16_t)hue;
			*pSaturations = (uint16_t)saturation;
			*pLights      = (uint16_t)light;
			
			pBluesRes++;
			pRedRes++;
			pGreenRes++;
			pHues++;
			pSaturations++;
			pLights++;
		}
		
		// Create binary string with motion result
		mp_obj_t objReds   = mp_obj_new_bytes((uint8_t *) motionDetector.reds  , motionDetector.max);
		mp_obj_t objGreens = mp_obj_new_bytes((uint8_t *) motionDetector.greens, motionDetector.max);
		mp_obj_t objBlues  = mp_obj_new_bytes((uint8_t *) motionDetector.blues , motionDetector.max);
		
		// Add the motion result in the list returned
		mp_obj_list_append(res, objReds  );
		mp_obj_list_append(res, objGreens);
		mp_obj_list_append(res, objBlues );
		
		// Build list of hue, saturation, light
		pHues        = motionDetector.hues;
		pSaturations = motionDetector.saturations;
		pLights      = motionDetector.lights;
		
		mp_obj_t objHues        = mp_obj_new_list(0, NULL);
		mp_obj_t objSaturations = mp_obj_new_list(0, NULL);
		mp_obj_t objLights      = mp_obj_new_list(0, NULL);
		for (i = 0; i < motionDetector.max; i++)
		{
			mp_obj_list_append(objHues       , mp_obj_new_int(*pHues));
			mp_obj_list_append(objSaturations, mp_obj_new_int(*pSaturations));
			mp_obj_list_append(objLights     , mp_obj_new_int(*pLights));
			pHues++;
			pSaturations++;
			pLights++;
		}
		
		// Add list of hues, saturations, lights
		mp_obj_list_append(res, objHues);
		mp_obj_list_append(res, objSaturations);
		mp_obj_list_append(res, objLights);
	}
	else
	{
		mp_raise_ValueError(MP_ERROR_TEXT("Camera esp_jpg_decode failed"));\
	}

	free(motionDetector.blues);
	free(motionDetector.reds);
	free(motionDetector.greens);

	free(motionDetector.hues);
	free(motionDetector.saturations);
	free(motionDetector.lights);
	
	return res;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_motion_detection_obj, camera_motion_detection);


STATIC mp_obj_t camera_pixformat(size_t n_args, const mp_obj_t *args)
{
	if (n_args == 0) 
	{
		sensor_t *s = esp_camera_sensor_get();
		if (s)
		{
			return mp_obj_new_int((int)s->pixformat);
		}
		else
		{
			mp_raise_ValueError(MP_ERROR_TEXT("Camera get pixformat not possible : driver not opened"));
		}
	}
	else
	{
		pixformat_t value = (pixformat_t)mp_obj_get_int(args[0]);
		if (value >= PIXFORMAT_RGB565 && value <= PIXFORMAT_RGB555)
		{
			sensor_t *s = esp_camera_sensor_get();
			if (s)
			{
				s->set_pixformat(s,(pixformat_t)value);
			}
			else
			{
				mp_raise_ValueError(MP_ERROR_TEXT("Camera set pixformat not possible : driver not opened"));
			}
		}
		else
		{
			mp_raise_ValueError(MP_ERROR_TEXT("Camera set pixformat : value out of limits [PIXFORMAT_RGB565-PIXFORMAT_RGB555]"));
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(camera_pixformat_obj, 0, 1, camera_pixformat);

#define CAMERA_SETTING(type, field, method, min, max) \
	STATIC mp_obj_t camera_##method(size_t n_args, const mp_obj_t *args)\
	{\
		if (n_args == 0) \
		{\
			sensor_t *s = esp_camera_sensor_get();\
			if (s)\
			{\
				return mp_obj_new_int((int)s->status.field);\
			}\
			else\
			{\
				mp_raise_ValueError(MP_ERROR_TEXT("Camera sensor get " #method " not possible : driver not opened"));\
			}\
		}\
		else\
		{\
			type value = (type)mp_obj_get_int(args[0]);\
			if (value >= min && value <= max)\
			{\
				sensor_t *s = esp_camera_sensor_get();\
				if (s)\
				{\
					s->set_ ## method(s,(type)value);\
				}\
				else\
				{\
					mp_raise_ValueError(MP_ERROR_TEXT("Camera sensor set " #method " not possible : driver not opened"));\
				}\
			}\
			else\
			{\
				mp_raise_ValueError(MP_ERROR_TEXT("Camera sensor set " #method " : value out of limits [" #min "-" #max "]"));\
			}\
		}\
		return mp_const_none;\
	}\
	STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(camera_##method##_obj, 0, 1, camera_##method);

#pragma GCC diagnostic ignored "-Wtype-limits"
//             type,        get             set           , min, max
CAMERA_SETTING(uint16_t   , aec_value     , aec_value     ,  0, 1200)
CAMERA_SETTING(framesize_t, framesize     , framesize     ,  FRAMESIZE_96X96, FRAMESIZE_QSXGA)
CAMERA_SETTING(uint8_t    , quality       , quality       ,  0, 63  )
CAMERA_SETTING(uint8_t    , special_effect, special_effect,  0, 6   )
CAMERA_SETTING(uint8_t    , wb_mode       , wb_mode       ,  0, 4   )
CAMERA_SETTING(uint8_t    , agc_gain      , agc_gain      ,  0, 30  )
CAMERA_SETTING(uint8_t    , gainceiling   , gainceiling   ,  0, 6   )
CAMERA_SETTING(int8_t     , brightness    , brightness    , -2, 2   )
CAMERA_SETTING(int8_t     , contrast      , contrast      , -2, 2   )
CAMERA_SETTING(int8_t     , saturation    , saturation    , -2, 2   )
CAMERA_SETTING(int8_t     , sharpness     , sharpness     , -2, 2   )
CAMERA_SETTING(int8_t     , ae_level      , ae_level      , -2, 2   )
CAMERA_SETTING(uint8_t    , denoise       , denoise       ,  0, 255 )
CAMERA_SETTING(uint8_t    , awb           , whitebal      ,  0, 255 )
CAMERA_SETTING(uint8_t    , awb_gain      , awb_gain      ,  0, 255 )
CAMERA_SETTING(uint8_t    , aec           , exposure_ctrl ,  0, 255 )
CAMERA_SETTING(uint8_t    , aec2          , aec2          ,  0, 255 )
CAMERA_SETTING(uint8_t    , agc           , gain_ctrl     ,  0, 255 )
CAMERA_SETTING(uint8_t    , bpc           , bpc           ,  0, 255 )
CAMERA_SETTING(uint8_t    , wpc           , wpc           ,  0, 255 )
CAMERA_SETTING(uint8_t    , raw_gma       , raw_gma       ,  0, 255 )
CAMERA_SETTING(uint8_t    , lenc          , lenc          ,  0, 255 )
CAMERA_SETTING(uint8_t    , hmirror       , hmirror       ,  0, 255 )
CAMERA_SETTING(uint8_t    , vflip         , vflip         ,  0, 255 )
CAMERA_SETTING(uint8_t    , dcw           , dcw           ,  0, 255 )
CAMERA_SETTING(uint8_t    , colorbar      , colorbar      ,  0, 255 )

#pragma GCC diagnostic pop

STATIC mp_obj_t camera_isavailable(){
#ifdef CONFIG_ESP32CAM
	return mp_const_true;
#else
	return mp_const_false;
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_isavailable_obj, camera_isavailable);



STATIC const mp_rom_map_elem_t camera_module_globals_table[] = {
	{ MP_ROM_QSTR(MP_QSTR___name__           ), MP_ROM_QSTR(MP_QSTR_camera) },
	{ MP_ROM_QSTR(MP_QSTR_init               ), MP_ROM_PTR(&camera_init_obj) },
	{ MP_ROM_QSTR(MP_QSTR_deinit             ), MP_ROM_PTR(&camera_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_capture            ), MP_ROM_PTR(&camera_capture_obj) },
	{ MP_ROM_QSTR(MP_QSTR_motion             ), MP_ROM_PTR(&camera_motion_detection_obj) },
	{ MP_ROM_QSTR(MP_QSTR_isavailable        ), MP_ROM_PTR(&camera_isavailable_obj) },

	{ MP_ROM_QSTR(MP_QSTR_pixformat          ), MP_ROM_PTR(&camera_pixformat_obj) },
	{ MP_ROM_QSTR(MP_QSTR_aec_value          ), MP_ROM_PTR(&camera_aec_value_obj) },
	{ MP_ROM_QSTR(MP_QSTR_framesize          ), MP_ROM_PTR(&camera_framesize_obj) },
	{ MP_ROM_QSTR(MP_QSTR_quality            ), MP_ROM_PTR(&camera_quality_obj) },
	{ MP_ROM_QSTR(MP_QSTR_special_effect     ), MP_ROM_PTR(&camera_special_effect_obj) },
	{ MP_ROM_QSTR(MP_QSTR_wb_mode            ), MP_ROM_PTR(&camera_wb_mode_obj) },
	{ MP_ROM_QSTR(MP_QSTR_agc_gain           ), MP_ROM_PTR(&camera_agc_gain_obj) },
	{ MP_ROM_QSTR(MP_QSTR_gainceiling        ), MP_ROM_PTR(&camera_gainceiling_obj) },
	{ MP_ROM_QSTR(MP_QSTR_brightness         ), MP_ROM_PTR(&camera_brightness_obj) },
	{ MP_ROM_QSTR(MP_QSTR_contrast           ), MP_ROM_PTR(&camera_contrast_obj) },
	{ MP_ROM_QSTR(MP_QSTR_saturation         ), MP_ROM_PTR(&camera_saturation_obj) },
	{ MP_ROM_QSTR(MP_QSTR_sharpness          ), MP_ROM_PTR(&camera_sharpness_obj) },
	{ MP_ROM_QSTR(MP_QSTR_ae_level           ), MP_ROM_PTR(&camera_ae_level_obj) },
	{ MP_ROM_QSTR(MP_QSTR_denoise            ), MP_ROM_PTR(&camera_denoise_obj) },
	{ MP_ROM_QSTR(MP_QSTR_whitebal           ), MP_ROM_PTR(&camera_whitebal_obj) },
	{ MP_ROM_QSTR(MP_QSTR_awb_gain           ), MP_ROM_PTR(&camera_awb_gain_obj) },
	{ MP_ROM_QSTR(MP_QSTR_exposure_ctrl      ), MP_ROM_PTR(&camera_exposure_ctrl_obj) },
	{ MP_ROM_QSTR(MP_QSTR_aec2               ), MP_ROM_PTR(&camera_aec2_obj) },
	{ MP_ROM_QSTR(MP_QSTR_gain_ctrl          ), MP_ROM_PTR(&camera_gain_ctrl_obj) },
	{ MP_ROM_QSTR(MP_QSTR_bpc                ), MP_ROM_PTR(&camera_bpc_obj) },
	{ MP_ROM_QSTR(MP_QSTR_wpc                ), MP_ROM_PTR(&camera_wpc_obj) },
	{ MP_ROM_QSTR(MP_QSTR_raw_gma            ), MP_ROM_PTR(&camera_raw_gma_obj) },
	{ MP_ROM_QSTR(MP_QSTR_lenc               ), MP_ROM_PTR(&camera_lenc_obj) },
	{ MP_ROM_QSTR(MP_QSTR_hmirror            ), MP_ROM_PTR(&camera_hmirror_obj) },
	{ MP_ROM_QSTR(MP_QSTR_vflip              ), MP_ROM_PTR(&camera_vflip_obj) },
	{ MP_ROM_QSTR(MP_QSTR_dcw                ), MP_ROM_PTR(&camera_dcw_obj) },
	{ MP_ROM_QSTR(MP_QSTR_colorbar           ), MP_ROM_PTR(&camera_colorbar_obj) },

	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_96X96    ), MP_ROM_INT(FRAMESIZE_96X96    )},  // 96x96
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_QQVGA    ), MP_ROM_INT(FRAMESIZE_QQVGA    )},  // 160x120
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_QCIF     ), MP_ROM_INT(FRAMESIZE_QCIF     )},  // 176x144
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_HQVGA    ), MP_ROM_INT(FRAMESIZE_HQVGA    )},  // 240x176
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_240X240  ), MP_ROM_INT(FRAMESIZE_240X240  )},  // 240x240
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_QVGA     ), MP_ROM_INT(FRAMESIZE_QVGA     )},  // 320x240
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_CIF      ), MP_ROM_INT(FRAMESIZE_CIF      )},  // 400x296
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_HVGA     ), MP_ROM_INT(FRAMESIZE_HVGA     )},  // 480x320
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_VGA      ), MP_ROM_INT(FRAMESIZE_VGA      )},  // 640x480
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_SVGA     ), MP_ROM_INT(FRAMESIZE_SVGA     )},  // 800x600
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_XGA      ), MP_ROM_INT(FRAMESIZE_XGA      )},  // 1024x768
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_HD       ), MP_ROM_INT(FRAMESIZE_HD       )},  // 1280x720
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_SXGA     ), MP_ROM_INT(FRAMESIZE_SXGA     )},  // 1280x1024
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_UXGA     ), MP_ROM_INT(FRAMESIZE_UXGA     )},  // 1600x1200
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_FHD      ), MP_ROM_INT(FRAMESIZE_FHD      )},  // 1920x1080
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_P_HD     ), MP_ROM_INT(FRAMESIZE_P_HD     )},  //  720x1280
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_P_3MP    ), MP_ROM_INT(FRAMESIZE_P_3MP    )},  //  864x1536
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_QXGA     ), MP_ROM_INT(FRAMESIZE_QXGA     )},  // 2048x1536
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_QHD      ), MP_ROM_INT(FRAMESIZE_QHD      )},  // 2560x1440
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_WQXGA    ), MP_ROM_INT(FRAMESIZE_WQXGA    )},  // 2560x1600
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_P_FHD    ), MP_ROM_INT(FRAMESIZE_P_FHD    )},  // 1080x1920
	{ MP_ROM_QSTR(MP_QSTR_FRAMESIZE_QSXGA    ), MP_ROM_INT(FRAMESIZE_QSXGA    )},  // 2560x1920

	{ MP_ROM_QSTR(MP_QSTR_PIXFORMAT_RGB565   ), MP_ROM_INT(PIXFORMAT_RGB565   )}, // 2BPP/RGB565
	{ MP_ROM_QSTR(MP_QSTR_PIXFORMAT_YUV422   ), MP_ROM_INT(PIXFORMAT_YUV422   )}, // 2BPP/YUV422
	{ MP_ROM_QSTR(MP_QSTR_PIXFORMAT_GRAYSCALE), MP_ROM_INT(PIXFORMAT_GRAYSCALE)}, // 1BPP/GRAYSCALE
	{ MP_ROM_QSTR(MP_QSTR_PIXFORMAT_JPEG     ), MP_ROM_INT(PIXFORMAT_JPEG     )}, // JPEG/COMPRESSED
	{ MP_ROM_QSTR(MP_QSTR_PIXFORMAT_RGB888   ), MP_ROM_INT(PIXFORMAT_RGB888   )}, // 3BPP/RGB888
	{ MP_ROM_QSTR(MP_QSTR_PIXFORMAT_RAW      ), MP_ROM_INT(PIXFORMAT_RAW      )}, // RAW
	{ MP_ROM_QSTR(MP_QSTR_PIXFORMAT_RGB444   ), MP_ROM_INT(PIXFORMAT_RGB444   )}, // 3BP2P/RGB444
	{ MP_ROM_QSTR(MP_QSTR_PIXFORMAT_RGB555   ), MP_ROM_INT(PIXFORMAT_RGB555   )}, // 3BP2P/RGB555
};

STATIC MP_DEFINE_CONST_DICT(camera_module_globals, camera_module_globals_table);

const mp_obj_module_t mp_module_camera = {
	.base = { &mp_type_module },
	.globals = (mp_obj_dict_t*)&camera_module_globals,
};
