// Code adapted from https://github.com/espressif/esp32-camera
#include "string.h"
#include "esp_log.h"
#include "esp_jpg_decode.h"
#include "esp_system.h"
#include "esp_spi_flash.h"

#include "py/nlr.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"
#include "py/objstr.h"

#ifdef CONFIG_ESP32CAM
	#include "esp_camera.h"
#endif
#define TAG "camera"

#define _ ESP_LOGE(TAG, "%s:%d:%s",__FILE__,__LINE__,__FUNCTION__);

#define min(a,b) ((a)<(b) ?(a):(b))
#define max(a,b) ((a)>(b) ?(a):(b))


#ifdef CONFIG_ESP32CAM

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

static camera_config_t camera_config = 
{
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
#endif

typedef struct Shape_t
{
	uint16_t id;
	uint32_t x;
	uint32_t y;
	uint16_t minx;
	uint16_t maxx;
	uint16_t miny;
	uint16_t maxy;
	uint16_t size;
} Shape_t;

#define MAX_POINTS 4
// Straight line portion
typedef struct 
{
	int x; // First x point of line
	int y; // First y point of line
	int a; // a * x + b
	int b;
} Line_t;
typedef struct 
{
	mp_obj_base_t base;

	uint8_t       *imageData;
	uint32_t       imageLength;
	uint16_t       height;
	uint16_t       width;
	const uint8_t *input;

	uint16_t       diffWidth;
	uint16_t       diffHeight;
	uint16_t       diffMax;

	uint16_t       square_x;
	uint16_t       square_y;

	uint16_t       *lights;

	uint16_t       *diffs;
	uint16_t       *stack;

#define MAX_HISTO 16
	uint16_t histo[MAX_HISTO];

	uint16_t       stackpos;
} Motion_t;
const mp_obj_type_t Motion_type;

typedef struct 
{
	uint8_t * mask_data;
	uint16_t  mask_length;
	Line_t errorLights[MAX_POINTS];
	Line_t errorHistos[MAX_POINTS];
} MotionConfiguration_t;

MotionConfiguration_t motionConfiguration = {0,0};
// Create motion objet with an image
static Motion_t * Motion_new(const uint8_t *imageData, size_t imageLength);


#pragma GCC diagnostic ignored "-Wtype-limits"
#ifdef CONFIG_ESP32CAM
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
#endif
#pragma GCC diagnostic pop

static void *_malloc(size_t size)
{
	void * result = heap_caps_calloc(1, size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
	if (result == 0)
	{
		ESP_LOGE(TAG, "Malloc failed !!!!!!");
	}
	return result;
}

static void _free(void ** ptr)
{
	if (ptr)
	{
		if (*ptr)
		{
			free(*ptr);
			*ptr = 0;
		}
	}
}

// Get list item at the index
mp_obj_t list_get_item(mp_obj_t list, size_t index)
{
	mp_obj_t result = mp_const_none;
	size_t length;
	mp_obj_t *items;
	mp_obj_list_get(list, &length, &items);

	if (index < length)
	{
		result = items[index];
	}
	return result;
}

size_t list_get_size(mp_obj_t list)
{
	size_t result = 0;
	mp_obj_t *items;
	mp_obj_list_get(list, &result, &items);
	return result;
}

#ifdef CONFIG_ESP32CAM
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
#endif

STATIC mp_obj_t camera_isavailable()
{
#ifdef CONFIG_ESP32CAM
	return mp_const_true;
#else
	return mp_const_false;
#endif
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_isavailable_obj, camera_isavailable);

#ifdef CONFIG_ESP32CAM
STATIC mp_obj_t camera_init()
{
	esp_err_t err = esp_camera_init(&camera_config);
	if (err != ESP_OK) 
	{
		ESP_LOGE(TAG, "Camera init failed");
		return mp_const_false;
	}

	return mp_const_true;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_init_obj, camera_init);

STATIC mp_obj_t camera_deinit()
{
	esp_err_t err = esp_camera_deinit();
	if (err != ESP_OK) 
	{
		ESP_LOGE(TAG, "Camera deinit failed");
		return mp_const_false;
	}
	return mp_const_true;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_deinit_obj, camera_deinit);

typedef struct 
{
	mp_obj_t       writeCallback;
	uint16_t       height;
	uint16_t       width;
	const uint8_t *input;
} Decoder_t;


static uint32_t camera_decodeRead(void * arg, size_t index, uint8_t *buf, size_t len)
{
	Decoder_t * decoder = (Decoder_t *)arg;
	if(buf) 
	{
		memcpy(buf, decoder->input + index, len);
	}
	return len;
}

//output buffer and image width
static bool camera_decodeImage(void * arg, uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint8_t *data)
{
	Decoder_t * decoder = (Decoder_t *)arg;
	
	// First access
	if(!data)
	{
		if(x == 0 && y == 0)
		{
			// Get the size of image
			decoder->width  = w;
			decoder->height = h;
		}
		else
		{
			// Write end
		}
	}
	else
	{
		int Y, X;
		//unsigned int red;
		//unsigned int green;
		//unsigned int blue;
		//uint8_t * pdata;
		ESP_LOGE(TAG, "Decode x=%d, y=%d, w=%d, h=%d",x,y,w,h);
		for (Y = y; Y < (y + h); Y ++)
		{
			for (X = x; X < (x + w); X ++) 
			{
				//pdata = &(data[(X-x)*3]);
				//blue  = *pdata; pdata++;
				//green = *pdata; pdata++;
				//red   = *pdata; pdata++;
			}
			data += (w * 3);
		}
	}
	return true;
}

// Decode image
STATIC mp_obj_t camera_decode(mp_obj_t image_in, mp_obj_t write_callback_in)
{
	if (mp_obj_is_str_or_bytes(image_in))
	{
		Decoder_t decoder;
		GET_STR_DATA_LEN(image_in, imageData, imageLength);
		memset(&decoder, 0, sizeof(decoder));
		decoder.input = imageData;

		if (write_callback_in != mp_const_none && !mp_obj_is_callable(write_callback_in)) 
		{
			mp_raise_ValueError(MP_ERROR_TEXT("Invalid write_callback"));
		}
		else
		{
			decoder.writeCallback = write_callback_in;
			esp_err_t ret = esp_jpg_decode(imageLength, JPG_SCALE_8X, camera_decodeRead, camera_decodeImage, (void*)&decoder);
			if (ret != ESP_OK)
			{
				mp_raise_ValueError(MP_ERROR_TEXT("Decoder error failed"));\
			}
		}
	}
	else
	{
		mp_raise_ValueError(MP_ERROR_TEXT("Invalid image buffer"));
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(camera_decode_obj, camera_decode);


STATIC mp_obj_t camera_capture()
{
	camera_fb_t * fb;

	// Acquire a frame
	fb = esp_camera_fb_get();
	if (!fb) 
	{
		ESP_LOGE(TAG, "Camera capture Failed");
		return mp_const_none;
	}
	mp_obj_t image = mp_obj_new_bytes(fb->buf, fb->len);

	// Return the frame buffer back to the driver for reuse
	esp_camera_fb_return(fb);
	return image;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_capture_obj, camera_capture);

// Get motion information
STATIC mp_obj_t camera_motion_detect()
{
	mp_obj_t res;
	camera_fb_t * fb;

	fb = esp_camera_fb_get();
	if (!fb) 
	{
		ESP_LOGE(TAG, "Camera capture Failed");
		return mp_const_none;
	}

	res = Motion_new(fb->buf, fb->len);

	esp_camera_fb_return(fb);
	return res;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(camera_motion_detect_obj, camera_motion_detect);

#endif

// input buffer
static uint32_t Motion_jpgRead(void * arg, size_t index, uint8_t *buf, size_t len)
{
	Motion_t * motion = (Motion_t *)arg;
	if(buf) 
	{
		memcpy(buf, motion->input + index, len);
	}
	return len;
}

//output buffer and image width
static bool Motion_parseImage(void * arg, uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint8_t *data)
{
	Motion_t * motion = (Motion_t *)arg;
	
	// First access
	if(!data)
	{
		if(x == 0 && y == 0)
		{
			// Get the size of image
			motion->width  = w;
			motion->height = h;

			if (((w/8) % 8) == 0)
			{
				motion->square_x = 8;
			}
			else
			{
				motion->square_x = 5;
			}

			if (((h/8) % 8) == 0)
			{
				motion->square_y = 8;
			}
			else
			{
				motion->square_y = 5;
			}

			motion->diffMax    = (w/motion->square_x) * (h/motion->square_y);
			motion->diffWidth  = (w/motion->square_x);
			motion->diffHeight = (h/motion->square_y);
			//ESP_LOGE(TAG, "motion %dx%d %dx%d %d",w,h, motion->square_x, motion->square_y, motion->diffMax);
			motion->lights      = (uint16_t*)_malloc(sizeof(uint16_t) * motion->diffMax);
			motion->diffs       = (uint16_t*)_malloc(sizeof(uint16_t) * motion->diffMax);
			motion->stack       = (uint16_t*)_malloc(sizeof(uint16_t) * motion->diffMax*2*4);
		}
		else
		{
			// Write end
		}
	}
	else
	{
		int Y, X;
		unsigned int red;
		unsigned int green;
		unsigned int blue;
		unsigned int light;
		uint16_t *lights;
		unsigned int square_x = motion->square_x;
		unsigned int square_y = motion->square_y;
		int posY;
		uint8_t * pdata;

		lights = motion->lights;

		// Compute the motion in the square detection
		for (Y = y; Y < (y + h); Y ++)
		{
			posY = ((Y/square_y)*(motion->width/square_x));
			for (X = x; X < (x + w); X ++) 
			{
				pdata = &(data[(X-x)*3]);
				blue  = *pdata; pdata++;
				green = *pdata; pdata++;
				red   = *pdata; pdata++;
				light = ((max(max(red,green),blue) + min(min(red,green),blue)) >> 1);
				motion->histo[light/MAX_HISTO] ++;
				lights[posY + (X / square_x)] += light;
			}
			data += (w * 3);
		}
	}
	return true;
}

unsigned long computeCrc(const uint8_t *imageData, size_t imageLength)
{
	unsigned long result =0;
	const unsigned long * ptrSrc = (unsigned long *)imageData;
	for (int i = 0; i < imageLength/4; i++)
	{
		result ^= *ptrSrc;
		ptrSrc ++;
	}
	return result;
}

// Create motion objet with an image
static Motion_t * Motion_new(const uint8_t *imageData, size_t imageLength)
{
	// Alloc class instance
	Motion_t *motion = m_new_obj_with_finaliser(Motion_t);
	if (motion)
	{
		memset(motion, 0, sizeof(Motion_t));
		motion->base.type = &Motion_type;
		motion->input = imageData;
		
		// Compute motion detection
		esp_err_t ret = esp_jpg_decode(imageLength, JPG_SCALE_8X, Motion_jpgRead, Motion_parseImage, (void*)motion);

		if (ret == ESP_OK)
		{
			int square = motion->square_x * motion->square_y;
			int i;
			motion->imageData = _malloc(max(imageLength, 64*1024)); // Max size image is 65536 limited by system
			if (motion->imageData)
			{
				motion->imageLength = imageLength;
				memcpy(motion->imageData, imageData, max(imageLength, 64*1024)); // Max size image is 65536 limited by system
			}

			for (i = 0; i < motion->diffMax; i++)
			{
				// Calculate the average on the detection square
				motion->lights[i] /= square;
			}
			for (i = 0; i < MAX_HISTO; i++)
			{
				motion->histo[i] /= square;
			}
		}
		else
		{
			mp_raise_ValueError(MP_ERROR_TEXT("Camera esp_jpg_decode failed"));\
		}
	}
	return motion;
}

// Constructor method
STATIC mp_obj_t Motion_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args)
{
	mp_obj_t  result = mp_const_none;
	enum
	{
		ARG_image,
	};
	// Constructor parameters
	static const mp_arg_t allowed_args[] = 
	{
		{ MP_QSTR_image,  MP_ARG_REQUIRED | MP_ARG_OBJ },
	};
	
	// Parsing parameters
	mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
	mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

	// Check image
	if (args[ARG_image].u_obj  == mp_const_none || ! mp_obj_is_str_or_bytes(args[ARG_image].u_obj))
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Bad image"));
	}
	else
	{
		GET_STR_DATA_LEN(args[ARG_image].u_obj, imageData, imageLength);

		Motion_t * self = Motion_new(imageData, imageLength);
		if (self)
		{
			result = self;
		}
	}
	return result;
}

// Delete method
STATIC mp_obj_t Motion_deinit(mp_obj_t self_in)
{
	Motion_t *motion = self_in;
	if (motion)
	{
		_free((void**)&motion->lights);
		_free((void**)&motion->diffs);
		_free((void**)&motion->imageData);
		_free((void**)&motion->stack);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(Motion_deinit_obj, Motion_deinit);

// extract method
STATIC mp_obj_t Motion_extract(mp_obj_t self_in)
{
	Motion_t *motion = self_in;
	mp_obj_t res = mp_obj_new_list(0, NULL);
	if (motion)
	{
		int i;
		uint16_t * pLights      = motion->lights;
		uint16_t * pDiffs       = motion->diffs;

		// Build list of light
		pLights      = motion->lights;
		pDiffs       = motion->diffs;
		
		mp_obj_t objLights      = mp_obj_new_list(0, NULL);
		mp_obj_t objDiffs       = mp_obj_new_list(0, NULL);
		for (i = 0; i < motion->diffMax; i++)
		{
			mp_obj_list_append(objLights     , mp_obj_new_int(*pLights));
			mp_obj_list_append(objDiffs      , mp_obj_new_int(*pDiffs));
			pLights++;
			pDiffs++;
		}

		mp_obj_t objHisto      = mp_obj_new_list(0,NULL);

		for (i = 0; i < MAX_HISTO; i++)
		{
			mp_obj_list_append(objHisto      , mp_obj_new_int(motion->histo[i]));
		}
		
		// Add image buffer
		mp_obj_list_append(res,mp_obj_new_bytes(motion->imageData, motion->imageLength));

		// Add list of lights
		mp_obj_list_append(res, objLights);

		// Add list with differences
		mp_obj_list_append(res, objDiffs);

		// Add list with histo
		mp_obj_list_append(res, objHisto);
	}

	return res;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(Motion_extract_obj, Motion_extract);

// getImage method
STATIC mp_obj_t Motion_getImage(mp_obj_t self_in)
{
	Motion_t *motion = self_in;
	mp_obj_t res = mp_const_none;
	if (motion)
	{
		res = mp_obj_new_bytes(motion->imageData, motion->imageLength);
	}
	return res;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(Motion_getImage_obj, Motion_getImage);

// getSize method
STATIC mp_obj_t Motion_getSize(mp_obj_t self_in)
{
	Motion_t *motion = self_in;
	mp_obj_t res = mp_const_none;
	if (motion)
	{
		res = mp_obj_new_int(motion->imageLength);
	}
	return res;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(Motion_getSize_obj, Motion_getSize);

// Push coordinates
void Motion_push(Motion_t * motion, int x, int y)
{
	motion->stack[motion->stackpos++] = x;
	motion->stack[motion->stackpos++] = y;
}

// Pop coordinates
void Motion_pop(Motion_t * motion, int *x, int *y)
{
	if (motion->stackpos > 0)
	{
		*y = motion->stack[--motion->stackpos];
		*x = motion->stack[--motion->stackpos];
	}
}

// Check if difference detected in the current pixel
bool Motion_isDifference(Motion_t * motion, int x, int y)
{
	bool result = false;

	// If position is in image
	if (x >= 0 && x < motion->width/motion->square_x && y >= 0 && y < motion->height/motion->square_y)
	{
		int i = y*(motion->width/motion->square_x) + x;
		uint16_t diff = motion->diffs[i];

		// If difference detected not yet found
		if (((diff & 0xFF00) == 0) && ((diff & 0xFF) != 0))
		{
			result = true;
		}
	}
	return result;
}

// Set the difference
void Motion_setDifference(Motion_t * motion, int x, int y, Shape_t * shape)
{
	int i = y*(motion->width/motion->square_x) + x;
	uint16_t diff = motion->diffs[i];

	// If difference not yet parsed
	if ((diff & 0xFF00) == 0)
	{
		// Modify current difference to add shape identifier
		motion->diffs[i] = (diff &0xFF) | (shape->id << 8);

		// Compute the difference informations
		shape->size ++;
		shape->x += x;
		shape->y += y;
		if (x < shape->minx) shape->minx = x;
		if (x > shape->maxx) shape->maxx = x;
		if (y < shape->miny) shape->miny = y;
		if (y > shape->maxy) shape->maxy = y;
	}
}

// Search a shape in the differences
bool Motion_searchShape(Motion_t * motion, int x, int y, Shape_t * shape)
{
	bool result = false;

	// Push coordinates
	motion->stackpos = 0;

	if (Motion_isDifference(motion, x, y))
	{
		Motion_push(motion, x,  y);
		
		while(motion->stackpos > 0)
		{
			// Pop coordinates
			Motion_pop(motion, &x, &y);
			
			Motion_setDifference(motion, x, y, shape);

			// Search in contigous pixels
			if (Motion_isDifference(motion, x+1,y  )) Motion_push(motion, x+1, y);
			if (Motion_isDifference(motion, x-1,y  )) Motion_push(motion, x-1, y);
			if (Motion_isDifference(motion, x  ,y+1)) Motion_push(motion, x  , y+1);
			if (Motion_isDifference(motion, x  ,y-1)) Motion_push(motion, x  , y-1);
			//if (Motion_isDifference(motion, x+1,y+1)) Motion_push(motion, x+1, y+1);
			//if (Motion_isDifference(motion, x-1,y+1)) Motion_push(motion, x-1, y+1);
			//if (Motion_isDifference(motion, x+1,y-1)) Motion_push(motion, x+1, y-1);
			//if (Motion_isDifference(motion, x-1,y-1)) Motion_push(motion, x-1, y-1);
		}
		result = true;
	}

	// Compute the center of shape
	if (shape->size > 0)
	{
		shape->x = shape->x / shape->size;
		shape->y = shape->y / shape->size;
		result = true;
	}
	return result;
}

// Compute histogram
int Motion_getDiffHisto(Motion_t *self, Motion_t *previous)
{
	int i;
	int diff = 0;
	for (i = 0; i < MAX_HISTO; i++)
	{
		diff += abs(self->histo[i] - previous->histo[i]);
	}

	if (diff > self->diffMax)
	{
		return 0;
	}
	else
	{
		return (256 - ((diff<< 8)/self->diffMax));
	}
}


/** Extract lines from the lists of points */
void Lines_configure(mp_obj_t points, Line_t * lines, int maxPoints)
{
	size_t size = list_get_size(points);

	if (maxPoints == size)
	{
		Line_t point1, point2;

		// For all points defined
		for (size_t i = 0; i < size; i++)
		{
			mp_obj_t point = list_get_item (points, i);

			// If x and y defined
			if (list_get_size(point) == 2)
			{
				// Get point of line
				point1.x = mp_obj_get_int(list_get_item(point, 0));
				point1.y = mp_obj_get_int(list_get_item(point, 1));

				// If it is not the first point of line
				if (i > 0)
				{
					// Save the point in the previous point
					point2 = lines[i-1];

					// If two points distincts
					if ((point1.x - point2.x) != 0)
					{
						// Compute the slope of line
						point1.a = (((point1.y - point2.y)<<8) / (point1.x - point2.x));
						point1.b = (point1.y - ((point1.a*point1.x)>>8));
					}
					else
					{
						mp_raise_TypeError(MP_ERROR_TEXT("Motions configure divide 0 for points"));
					}
				}
				else
				{
					point1.a = 0;
					point1.b = 0;
				}
				// ESP_LOGE(TAG,"x=%d y=%d a=%d b=%d",point1.x, point1.y, point1.a, point1.b);
				lines[i] = point1;
			}
		}
	}
	else
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Motions bad configure size for points"));
	}
}

/** Compute Y value according to X */
int Lines_getY(Line_t * lines, int maxPoints, int x)
{
	int i;
	int y =0;

	// Search the error x according to the x level
	for (i = 1; i < maxPoints; i++)
	{
		// If right straight line found
		if (x >= lines[i-1].x && x < lines[i].x)
		{
			// Compute the error light according its position in the straight line
			y =((lines[i].a * x)>>8) + lines[i].b;
			break;
		}
	}
	return y;
}

// Compute the difference between two motion detection
STATIC int Motion_computeDiff(Motion_t *self, Motion_t *previous, mp_obj_t result)
{
	int i;
	int diffDetected = 0;
	int diffHisto    = Motion_getDiffHisto(self, previous);
	int errLight;
	int errHisto;
	uint16_t       *pCurrentLights  = self->lights;
	uint16_t       *pPreviousLights = previous->lights;
	uint16_t       *pDiffs          = self->diffs;
	int light;

	// Compute the error histo according to the curves configured
	errHisto = Lines_getY(motionConfiguration.errorHistos, MAX_POINTS, diffHisto);

	// For all square detection
	for (i = 0; i < self->diffMax; i++)
	{
		// Get the current max light of the selected square for two motion images
		light = max(*pCurrentLights, *pPreviousLights);

		// Compute the error light according to the curves configured
		errLight = Lines_getY(motionConfiguration.errorLights, MAX_POINTS, light);

		// Mitigate the error according to the change in brightness
		if (((abs(*pCurrentLights - *pPreviousLights) * errHisto)>>8) > errLight)
		{
			*pDiffs = 0x01;
			diffDetected ++;
		}
		pDiffs ++;
		pCurrentLights ++;
		pPreviousLights ++;
	}

	char * diffs = (char*)_malloc(sizeof(char) * self->diffMax + 1);
	if (motionConfiguration.mask_length > 0 && motionConfiguration.mask_length == self->diffMax)
	{
		int ignored = 0;
		uint8_t * pMask = motionConfiguration.mask_data;
		pDiffs         = self->diffs;
		for (i = 0; i < self->diffMax; i++)
		{
			if (*pDiffs)
			{
				if (*pMask == '/')
				{
					diffs[i] = ' ';
					diffDetected --;
					ignored ++;
					*pDiffs = 0;
					// ESP_LOGE(TAG,"ignored = %d %c %d", i, *pMask, diffDetected);
				}
				else
				{
					diffs[i] = '#';
				}
			}
			else
			{
				diffs[i] = ' ';
			}
			pDiffs++;
			pMask++;
		}
		//ESP_LOGE(TAG,"ignored=%d diff=%d",  ignored, diffDetected);
	}
	else
	{
		pDiffs         = self->diffs;
		for (i = 0; i < self->diffMax; i++)
		{
			if (*pDiffs)
			{
				diffs[i] = '#';
			}
			else
			{
				diffs[i] = ' ';
			}
			pDiffs++;
		}
	}

	mp_obj_t diffdict = mp_obj_new_dict(0);
		mp_obj_dict_store(diffdict, mp_obj_new_str("count"     , strlen("count"))     ,  mp_obj_new_int(diffDetected));
		mp_obj_dict_store(diffdict, mp_obj_new_str("max"       , strlen("max"))       ,  mp_obj_new_int(self->diffMax));
		mp_obj_dict_store(diffdict, mp_obj_new_str("squarex"   , strlen("squarex"))   ,  mp_obj_new_int(self->square_x*8));
		mp_obj_dict_store(diffdict, mp_obj_new_str("squarey"   , strlen("squarey"))   ,  mp_obj_new_int(self->square_y*8));
		mp_obj_dict_store(diffdict, mp_obj_new_str("width"     , strlen("width"))     ,  mp_obj_new_int(self->diffWidth));
		mp_obj_dict_store(diffdict, mp_obj_new_str("height"    , strlen("height"))    ,  mp_obj_new_int(self->diffHeight));
		mp_obj_dict_store(diffdict, mp_obj_new_str("diffhisto" , strlen("diffhisto")) ,  mp_obj_new_int(diffHisto));
		mp_obj_dict_store(diffdict, mp_obj_new_str("errhisto"  , strlen("errhisto"))  ,  mp_obj_new_int(errHisto));
		mp_obj_dict_store(diffdict, mp_obj_new_str("diffs"     , strlen("diffs"))     ,  mp_obj_new_str(diffs     , self->diffMax));
	mp_obj_dict_store(result, mp_obj_new_str("diff"     , strlen("diff")), diffdict);
	_free((void**)&diffs);
	return diffDetected;
}

STATIC void Motion_extractShape(Motion_t *self, mp_obj_t result, bool extractShape)
{
	int x;
	int y;
	int width  = self->width /self->square_x;
	int height = self->height/self->square_y;

	// Get the list of shapes detected
	mp_obj_t shapeslist = mp_obj_new_list(0, NULL);

	if (extractShape)
	{
		Shape_t shape;
		int shapeId = 1;

		for (y = 0; y < height; y++)
		{
			for (x = 0; x < width; x++)
			{
				memset(&shape, 0, sizeof(shape));
				shape.minx = self->diffMax;
				shape.miny = self->diffMax;
				shape.id = shapeId;

				// If shape found
				if (Motion_searchShape(self, x, y,&shape))
				{
					mp_obj_t shapedict = mp_obj_new_dict(0);
						mp_obj_dict_store(shapedict, mp_obj_new_str("size",    strlen("size")),     mp_obj_new_int(shape.size));
	#if 1
						mp_obj_dict_store(shapedict, mp_obj_new_str("centerx", strlen("centerx")),  mp_obj_new_int(shape.x*self->square_x*8));
						mp_obj_dict_store(shapedict, mp_obj_new_str("centery", strlen("centery")),  mp_obj_new_int(shape.y*self->square_y*8));
						mp_obj_dict_store(shapedict, mp_obj_new_str("x",       strlen("x")),        mp_obj_new_int(shape.minx*self->square_x*8));
						mp_obj_dict_store(shapedict, mp_obj_new_str("y",       strlen("y")),        mp_obj_new_int(shape.miny*self->square_y*8));
						mp_obj_dict_store(shapedict, mp_obj_new_str("width",   strlen("width")),    mp_obj_new_int((shape.maxx + 1 - shape.minx)*self->square_x*8));
						mp_obj_dict_store(shapedict, mp_obj_new_str("height",  strlen("height")),   mp_obj_new_int((shape.maxy + 1 - shape.miny)*self->square_y*8));
	#else
						mp_obj_dict_store(shapedict, mp_obj_new_str("centerx", strlen("centerx")),  mp_obj_new_int(shape.x));
						mp_obj_dict_store(shapedict, mp_obj_new_str("centery", strlen("centery")),  mp_obj_new_int(shape.y));
						mp_obj_dict_store(shapedict, mp_obj_new_str("minx",    strlen("minx")),     mp_obj_new_int(shape.minx));
						mp_obj_dict_store(shapedict, mp_obj_new_str("miny",    strlen("miny")),     mp_obj_new_int(shape.miny));
						mp_obj_dict_store(shapedict, mp_obj_new_str("maxx",    strlen("maxx")),     mp_obj_new_int(shape.maxx));
						mp_obj_dict_store(shapedict, mp_obj_new_str("maxy",    strlen("maxy")),     mp_obj_new_int(shape.maxy));
	#endif
						mp_obj_dict_store(shapedict, mp_obj_new_str("id",      strlen("id")),       mp_obj_new_int(shape.id));
					mp_obj_list_append(shapeslist, shapedict);
					shapeId++;
				}
			}
		}
		#if 0
		{
			char line[100];
			int i;

			for (y = 0; y < height; y++)
			{
				for (x = 0; x < width; x++)
				{
					i = y * width + x;
					if (self->diffs[i])
					{
						line[x] = ((self->diffs[i]&0xFF00)>>8) + 0x30;
						line[x+1] = '\0';
					}
					else
					{
						line[x] = ' ';
						line[x+1] = '\0';
					}
				}
				ESP_LOGE(TAG,"|%s|",line);
			}
		}
		#endif
	}
	mp_obj_dict_store(result, mp_obj_new_str("shapes"      , strlen("shapes")) , shapeslist);
}

// compare method
STATIC mp_obj_t Motion_compare(mp_obj_t self_in, mp_obj_t other_in, mp_obj_t extract_shape_in)
{
	Motion_t *self = self_in;
	Motion_t *previous = other_in;

	if (previous->base.type != &Motion_type)
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Not motion object"));
	}
	else if (self->diffMax != previous->diffMax)
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Motions not same format"));
	}
	else if (!mp_obj_is_bool(extract_shape_in) && extract_shape_in != mp_const_none)
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Motions bad parameters"));
	}
	else
	{
		int extractShape = mp_obj_is_true(extract_shape_in);

		mp_obj_t result = mp_obj_new_dict(0);

		if (Motion_computeDiff(self, previous, result) > 0)
		{
			Motion_extractShape(self, result, extractShape);
		}

		mp_obj_t geometrydict = mp_obj_new_dict(0);
			mp_obj_dict_store(geometrydict, mp_obj_new_str("width",   strlen("width")),    mp_obj_new_int(self->width  * 8));
			mp_obj_dict_store(geometrydict, mp_obj_new_str("height",  strlen("height")),   mp_obj_new_int(self->height * 8));
		mp_obj_dict_store(result, mp_obj_new_str("geometry"     , strlen("geometry")), geometrydict);

		return result;
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(Motion_compare_obj, Motion_compare);



// configure method
STATIC mp_obj_t Motion_configure(mp_obj_t self_in, mp_obj_t params_in)
{
	Motion_t *self = self_in;

	if (self->base.type != &Motion_type)
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Not motion object"));
	}
	else if (!mp_obj_is_dict_or_ordereddict(params_in) && params_in != mp_const_none)
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Motions bad parameters"));
	}
	else
	{
		mp_obj_t errorLights = mp_obj_dict_get(params_in, MP_OBJ_NEW_QSTR(MP_QSTR_errorLights));
		Lines_configure(errorLights, motionConfiguration.errorLights, MAX_POINTS);

		mp_obj_t errorHistos = mp_obj_dict_get(params_in, MP_OBJ_NEW_QSTR(MP_QSTR_errorHistos));
		Lines_configure(errorHistos, motionConfiguration.errorHistos, MAX_POINTS);

		mp_obj_t mask_in = mp_obj_dict_get(params_in, MP_OBJ_NEW_QSTR(MP_QSTR_mask));
		if (mp_obj_is_str_or_bytes(mask_in))
		{
			GET_STR_DATA_LEN(mask_in, mask_data, mask_length);
			if (motionConfiguration.mask_data)
			{
				_free((void**)&motionConfiguration.mask_data);
				motionConfiguration.mask_data = 0;
				motionConfiguration.mask_length = 0;
			}

			if (mask_length > 0)
			{
				motionConfiguration.mask_data = _malloc(mask_length + 1);
				if (motionConfiguration.mask_data)
				{
					memcpy(motionConfiguration.mask_data, mask_data, mask_length);
					motionConfiguration.mask_length = mask_length;
					motionConfiguration.mask_data[mask_length] = '\0';
					//ESP_LOGE(TAG,"|%s|",motionConfiguration.mask_data);
				}
			}
		}
		else
		{
			mp_raise_TypeError(MP_ERROR_TEXT("Bad mask type"));
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Motion_configure_obj, Motion_configure);

// print method
STATIC void Motion_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) 
{
	ESP_LOGE(TAG, "Motion_print");
}

// Methods
STATIC const mp_rom_map_elem_t Motion_locals_dict_table[] = 
{
	// Delete method
	{ MP_ROM_QSTR(MP_QSTR___del__),            MP_ROM_PTR(&Motion_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_deinit),             MP_ROM_PTR(&Motion_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_extract),            MP_ROM_PTR(&Motion_extract_obj) },
	{ MP_ROM_QSTR(MP_QSTR_compare),            MP_ROM_PTR(&Motion_compare_obj) },
	{ MP_ROM_QSTR(MP_QSTR_configure),          MP_ROM_PTR(&Motion_configure_obj) },
	{ MP_ROM_QSTR(MP_QSTR_getImage),           MP_ROM_PTR(&Motion_getImage_obj) },
	{ MP_ROM_QSTR(MP_QSTR_getSize),            MP_ROM_PTR(&Motion_getSize_obj) },
};
STATIC MP_DEFINE_CONST_DICT(Motion_locals_dict, Motion_locals_dict_table);

// Class definition
const mp_obj_type_t Motion_type = 
{
	{ &mp_type_type },
	.name        = MP_QSTR_Motion,
	.print       = Motion_print,
	.make_new    = Motion_make_new,
	.locals_dict = (mp_obj_t)&Motion_locals_dict,
};

STATIC const mp_rom_map_elem_t camera_module_globals_table[] = {
	{ MP_ROM_QSTR(MP_QSTR___name__           ), MP_ROM_QSTR(MP_QSTR_camera) },
	{ MP_ROM_QSTR(MP_QSTR_isavailable        ), MP_ROM_PTR(&camera_isavailable_obj) },
#ifdef CONFIG_ESP32CAM
	{ MP_ROM_QSTR(MP_QSTR_init               ), MP_ROM_PTR(&camera_init_obj) },
	{ MP_ROM_QSTR(MP_QSTR_deinit             ), MP_ROM_PTR(&camera_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_capture            ), MP_ROM_PTR(&camera_capture_obj) },
	{ MP_ROM_QSTR(MP_QSTR_motion             ), MP_ROM_PTR(&camera_motion_detect_obj) },
	{ MP_ROM_QSTR(MP_QSTR_decode             ), MP_ROM_PTR(&camera_decode_obj) },
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
#endif
	{ MP_ROM_QSTR(MP_QSTR_Motion             ), MP_ROM_PTR(&Motion_type) },
};
STATIC MP_DEFINE_CONST_DICT(camera_module_globals, camera_module_globals_table);

const mp_obj_module_t mp_module_camera = 
{
	.base = { &mp_type_module },
	.globals = (mp_obj_dict_t*)&camera_module_globals,
};
