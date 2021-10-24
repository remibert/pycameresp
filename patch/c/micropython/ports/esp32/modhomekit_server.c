/* Distributed under MIT License
Copyright (c) 2021 Remi BERTHOLET */
#include "modhomekit.h"

#define TAG "Homekit"

// Objet classe python
typedef struct 
{
	mp_obj_base_t base;
	hap_serv_t *  server;
} Server_t;

const mp_obj_type_t Server_type;


// Get the pointer of server
hap_serv_t * Server_get_ptr(mp_obj_t self_in)
{
	hap_serv_t * result = 0;
	Server_t *self = self_in;
	if (self->base.type == &Server_type)
	{
		result = self->server;
	}
	return result;
}


// Read callback
static int Server_read_callback(hap_char_t *hc, hap_status_t *status_code, void *serv_priv, void *read_priv)
{
	*status_code = Charact_read_call(hc);
	return HAP_SUCCESS;
}


// Write callback
static int Server_write_callback(hap_write_data_t write_data[], int count, void *serv_priv, void *write_priv)
{
	int i, ret = HAP_SUCCESS;
	hap_write_data_t *write;
	for (i = 0; i < count; i++) 
	{
		write = &write_data[i];
		*(write->status) = Charact_write_call(write->hc, &(write->val));
	}
	return ret;
}


// Constructor method
STATIC mp_obj_t Server_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args)
{
	mp_obj_t  result = mp_const_none;
	enum 
	{
		ARG_uuid,
	};
	// Constructor parameters
	static const mp_arg_t allowed_args[] = 
	{
		{ MP_QSTR_uuid,  MP_ARG_REQUIRED | MP_ARG_OBJ },
	};
	
	// Parsing parameters
	mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
	mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

	// Check uuid
	if (args[ARG_uuid].u_obj  == mp_const_none || ! mp_obj_is_str(args[ARG_uuid].u_obj))
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Bad uuid"));
	}
	else
	{
		// Alloc class instance
		Server_t *self = m_new_obj_with_finaliser(Server_t);
		if (self)
		{
			self->server = 0;
			self->base.type = &Server_type;
			result = self;
			GET_STR_DATA_LEN(args[ARG_uuid].u_obj , uuid, uuid_len);
			self->server = hap_serv_create((char*)uuid);
			hap_serv_set_priv(self->server, self);

			// Set the write callback for the service
			hap_serv_set_write_cb(self->server, Server_write_callback);

			// Set the read callback for the service (optional)
			hap_serv_set_read_cb(self->server, Server_read_callback);
		}
	}
	return result;
}


// Delete method
STATIC mp_obj_t Server_deinit(mp_obj_t self_in)
{
	Server_t *self = self_in;
	if (self->server)
	{
		hap_serv_delete(self->server);
	}
	
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(Server_deinit_obj, Server_deinit);


// add_charact method
STATIC mp_obj_t Server_add_charact(mp_obj_t self_in, mp_obj_t charact_in)
{
	Server_t *self = self_in;
	if (self->server)
	{
		hap_char_t * charact = Charact_get_ptr(charact_in);
		if (charact)
		{
			hap_serv_add_char(self->server, charact);
		}
		else
		{
			mp_raise_TypeError(MP_ERROR_TEXT("Not Charact type"));
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Server_add_charact_obj, Server_add_charact);


// print method
STATIC void Server_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) 
{
	//ESP_LOGE(TAG, "Server_print");
}


// Methods
STATIC const mp_rom_map_elem_t Server_locals_dict_table[] = 
{
	// Delete method
	{ MP_ROM_QSTR(MP_QSTR___del__),         MP_ROM_PTR(&Server_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_deinit),          MP_ROM_PTR(&Server_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_add_charact),      MP_ROM_PTR(&Server_add_charact_obj) },
};
STATIC MP_DEFINE_CONST_DICT(Server_locals_dict, Server_locals_dict_table);


// Class definition
const mp_obj_type_t Server_type = 
{
	{ &mp_type_type },
	.name        = MP_QSTR_Server,
	.print       = Server_print,
	.make_new    = Server_make_new,
	.locals_dict = (mp_obj_t)&Server_locals_dict,
};

