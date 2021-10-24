/* Distributed under MIT License
Copyright (c) 2021 Remi BERTHOLET */
#include "modhomekit.h"

#define TAG "Homekit"


static mp_obj_t   identifyCallback = mp_const_none;

// Objet classe python
typedef struct 
{
	mp_obj_base_t base;
	hap_acc_t *   accessory;
	char          name         [32];
	char          manufacturer [32];
	char          model        [32];
	char          serial_number[16];
	char          firmware_revision       [16];
	char          hardware_revision       [16];
	char          product_version [16];
	uint8_t       productData[8];
} Accessory_t;

const mp_obj_type_t Accessory_type;


// Get the pointer of accessory
hap_acc_t * Accessory_get_ptr(mp_obj_t self_in)
{
	hap_acc_t * result = 0;
	Accessory_t *self = self_in;
	if (self->base.type == &Accessory_type)
	{
		result = self->accessory;
	}
	return result;
}


static int Accessory_identify(hap_acc_t *ha)
{
	//ESP_LOGE(TAG, "Accessory_identify");
	if (identifyCallback != mp_const_none)
	{
		mp_sched_schedule(identifyCallback, mp_const_none);
		mp_hal_wake_main_task_from_isr();
	}

	return HAP_SUCCESS;
}

#define ACCESSORY_SET(id) \
	if (args[ARG_##id].u_obj != mp_const_none) \
	{\
		size_t len;\
		const char *p = mp_obj_str_get_data(args[ARG_##id].u_obj, &len);\
		len = MIN(len, sizeof(self->id));\
		memcpy(self->id, p, len);\
	}\
	else\
	{\
		self->id[0] = '\0';\
	}

// Constructor method
STATIC mp_obj_t Accessory_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args)
{
	mp_obj_t  result = mp_const_none;
	enum 
	{ 
		ARG_cid,
		ARG_name,
		ARG_manufacturer,
		ARG_model,
		ARG_serial_number,
		ARG_firmware_revision,
		ARG_hardware_revision,
		ARG_product_version,
	};

	// Constructor parameters
	static const mp_arg_t allowed_args[] = 
	{
		{ MP_QSTR_cid,                MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = HAP_CID_OTHER} },
		{ MP_QSTR_name,               MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_rom_obj = MP_ROM_QSTR(MP_QSTR__Esp)} },
		{ MP_QSTR_manufacturer,       MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_rom_obj = MP_ROM_QSTR(MP_QSTR__Espressif)} },
		{ MP_QSTR_model,              MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_rom_obj = MP_ROM_QSTR(MP_QSTR__Esp32)} },
		{ MP_QSTR_serial_number,      MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_rom_obj = MP_ROM_QSTR(MP_QSTR__000000000000)} },
		{ MP_QSTR_firmware_revision,  MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_rom_obj = MP_ROM_QSTR(MP_QSTR__1)} },
		{ MP_QSTR_hardware_revision,  MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_rom_obj = MP_ROM_QSTR(MP_QSTR__1)} },
		{ MP_QSTR_product_version,    MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_rom_obj = MP_ROM_QSTR(MP_QSTR__1)} },
	};
	
	// Parsing parameters
	mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
	mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

	// Alloc class instance
	Accessory_t *self = m_new_obj_with_finaliser(Accessory_t);
	if (self)
	{
		self->accessory = 0;
		self->base.type = &Accessory_type;
		result = self;

		ACCESSORY_SET(name)
		ACCESSORY_SET(manufacturer)
		ACCESSORY_SET(model)
		ACCESSORY_SET(serial_number)
		ACCESSORY_SET(firmware_revision)
		ACCESSORY_SET(hardware_revision)
		ACCESSORY_SET(product_version)

		hap_acc_cfg_t cfg = 
		{
			.name             = self->name,
			.manufacturer     = self->manufacturer,
			.model            = self->model,
			.serial_num       = self->serial_number,
			.fw_rev           = self->firmware_revision,
			.hw_rev           = self->hardware_revision,
			.pv               = self->product_version,
			.identify_routine = Accessory_identify,
			.cid              = args[ARG_cid].u_int,
		};

		// Create accessory object
		self->accessory = hap_acc_create(&cfg);
	}
	return result;
}


// Delete method
STATIC mp_obj_t Accessory_deinit(mp_obj_t self_in)
{
	Accessory_t *self = self_in;
	if (self->accessory)
	{
		hap_acc_delete(self->accessory);
	}
	
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(Accessory_deinit_obj, Accessory_deinit);


// add_server method
STATIC mp_obj_t Accessory_add_server(mp_obj_t self_in, mp_obj_t server_in)
{
	Accessory_t *self = self_in;
	// ESP_LOGE(TAG, "Accessory_add_server");
	if (self->accessory)
	{
		hap_serv_t * server = Server_get_ptr(server_in);
		if (server)
		{
			hap_acc_add_serv(self->accessory, server);
		}
		else
		{
			mp_raise_TypeError(MP_ERROR_TEXT("Not Server type"));
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Accessory_add_server_obj, Accessory_add_server);


// set_identify callback method
STATIC mp_obj_t Accessory_set_identify_callback(mp_obj_t self_in, mp_obj_t identify_callback_in)
{
	Accessory_t *self = self_in;

	if (self->accessory)
	{
		if (identify_callback_in == mp_const_none || mp_obj_is_callable(identify_callback_in)) 
		{
			identifyCallback = identify_callback_in;
		}
		else
		{
			mp_raise_ValueError(MP_ERROR_TEXT("invalid identify_callback"));
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Accessory_set_identify_callback_obj, Accessory_set_identify_callback);



// set_identify callback method
STATIC mp_obj_t Accessory_set_product_data(mp_obj_t self_in, mp_obj_t product_data_in)
{
	Accessory_t *self = self_in;

	if (self->accessory)
	{
		GET_STR_DATA_LEN(product_data_in , product_data, product_data_len);
		memcpy(self->productData, product_data, MIN(product_data_len, sizeof(self->productData)));
		if (product_data_len == 8)
		{
			hap_acc_add_product_data(self->accessory, self->productData, sizeof(self->productData));
		}
		else
		{
			mp_raise_TypeError(MP_ERROR_TEXT("Must be a string with 8 bytes"));
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Accessory_set_product_data_obj, Accessory_set_product_data);


// print method
STATIC void Accessory_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) 
{
	//ESP_LOGE(TAG, "Accessory_print");
}


// Methods
STATIC const mp_rom_map_elem_t Accessory_locals_dict_table[] = 
{
	// Delete method
	{ MP_ROM_QSTR(MP_QSTR___del__),                MP_ROM_PTR(&Accessory_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_deinit),                 MP_ROM_PTR(&Accessory_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_add_server),             MP_ROM_PTR(&Accessory_add_server_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_identify_callback),  MP_ROM_PTR(&Accessory_set_identify_callback_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_product_data),       MP_ROM_PTR(&Accessory_set_product_data_obj) },
};
STATIC MP_DEFINE_CONST_DICT(Accessory_locals_dict, Accessory_locals_dict_table);


// Class definition
const mp_obj_type_t Accessory_type = 
{
	{ &mp_type_type },
	.name        = MP_QSTR_Accessory,
	.print       = Accessory_print,
	.make_new    = Accessory_make_new,
	.locals_dict = (mp_obj_t)&Accessory_locals_dict,
};

