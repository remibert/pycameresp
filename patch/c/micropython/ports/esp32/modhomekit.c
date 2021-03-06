/* Distributed under MIT License
Copyright (c) 2021 Remi BERTHOLET */
#include "modhomekit.h"

#define TAG "Homekit"

STATIC mp_obj_t homekit_init()
{
	int res;
	hap_cfg_t hap_cfg;
	hap_get_config(&hap_cfg);
	hap_cfg.unique_param = UNIQUE_NAME;
	hap_set_config(&hap_cfg);

	res = hap_init(HAP_TRANSPORT_WIFI);
	if (res != HAP_SUCCESS)
	{
		mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("Init failed err=%d"), res);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(homekit_init_obj, homekit_init);


STATIC mp_obj_t homekit_start()
{
	int res;

	// Enable Hardware MFi authentication (applicable only for MFi variant of SDK)
	hap_enable_mfi_auth(HAP_MFI_AUTH_HW);

	res = hap_start();
	if (res != HAP_SUCCESS)
	{
		mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("Start failed err=%d"), res);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(homekit_start_obj, homekit_start);


STATIC mp_obj_t homekit_stop()
{
	int res = hap_stop();
	if (res != HAP_SUCCESS)
	{
		mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("Stop failed err=%d"), res);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(homekit_stop_obj, homekit_stop);

STATIC mp_obj_t homekit_setSetupId(const mp_obj_t setup_id_in)
{
	GET_STR_DATA_LEN(setup_id_in, setup_id, setup_id_len);
	if (setup_id_len == 4)
	{
		hap_set_setup_id((const char *)setup_id);
	}
	else
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Setup id bad length must be 4 bytes"));
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(homekit_setSetupId_obj, homekit_setSetupId);


STATIC mp_obj_t homekit_setSetupCode(const mp_obj_t setup_code_in)
{
	GET_STR_DATA_LEN(setup_code_in, setup_code, setup_code_len);
	if (setup_code_len == 10 && setup_code[3] == '-' && setup_code[6] == '-')
	{
		hap_set_setup_code((const char *)setup_code);
	}
	else
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Setup code bad format must be 'xxx-xx-xxx'"));
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(homekit_setSetupCode_obj, homekit_setSetupCode);


STATIC mp_obj_t homekit_addAccessory(const mp_obj_t accessory_in)
{
	hap_acc_t * accessory = Accessory_get_ptr(accessory_in);

	if (accessory)
	{
		hap_add_accessory(accessory);
	}
	else
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Not an Accessory instance"));
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(homekit_addAccessory_obj, homekit_addAccessory);


STATIC mp_obj_t homekit_deinit()
{
	int res = hap_deinit();
	if (res != HAP_SUCCESS)
	{
		mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("Deinit failed err=%d"), res);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(homekit_deinit_obj, homekit_deinit);

STATIC mp_obj_t homekit_eraseAll()
{
	hap_stop();
	hap_deinit();
	hap_keystore_erase_all_data();
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(homekit_eraseAll_obj, homekit_eraseAll);



STATIC const mp_rom_map_elem_t homekit_module_globals_table[] = 
{
	{ MP_ROM_QSTR(MP_QSTR___name__           ), MP_ROM_QSTR(MP_QSTR_homekit) },
	{ MP_ROM_QSTR(MP_QSTR_init               ), MP_ROM_PTR(&homekit_init_obj) },
	{ MP_ROM_QSTR(MP_QSTR_deinit             ), MP_ROM_PTR(&homekit_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_eraseAll           ), MP_ROM_PTR(&homekit_eraseAll_obj) },
	{ MP_ROM_QSTR(MP_QSTR_start              ), MP_ROM_PTR(&homekit_start_obj) },
	{ MP_ROM_QSTR(MP_QSTR_stop               ), MP_ROM_PTR(&homekit_stop_obj) },
	{ MP_ROM_QSTR(MP_QSTR_setSetupId         ), MP_ROM_PTR(&homekit_setSetupId_obj) },
	{ MP_ROM_QSTR(MP_QSTR_setSetupCode       ), MP_ROM_PTR(&homekit_setSetupCode_obj) },
	{ MP_ROM_QSTR(MP_QSTR_addAccessory       ), MP_ROM_PTR(&homekit_addAccessory_obj) },
	{ MP_ROM_QSTR(MP_QSTR_Charact            ), MP_ROM_PTR(&Charact_type) },
	{ MP_ROM_QSTR(MP_QSTR_Server             ), MP_ROM_PTR(&Server_type) },
	{ MP_ROM_QSTR(MP_QSTR_Accessory          ), MP_ROM_PTR(&Accessory_type) },
};

STATIC MP_DEFINE_CONST_DICT(homekit_module_globals, homekit_module_globals_table);

const mp_obj_module_t mp_module_homekit = 
{
	.base = { &mp_type_module },
	.globals = (mp_obj_dict_t*)&homekit_module_globals,
};
