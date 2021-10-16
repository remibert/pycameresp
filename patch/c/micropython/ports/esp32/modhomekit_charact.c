/* Distributed under MIT License
Copyright (c) 2021 Remi BERTHOLET */
#include "modhomekit.h"

#define TAG "Homekit"

#define TYPE_INT    0
#define TYPE_BOOL   1
#define TYPE_FLOAT  2
#define TYPE_UINT32 3
#define TYPE_STRING 4
#define TYPE_UINT8  5
#define TYPE_MAX    6

// Objet classe python
typedef struct 
{
	mp_obj_base_t base;
	int           type;
	int           min;
	int           max;
	int           step;
	float         min_f;
	float         max_f;
	float         step_f;
	hap_char_t *  charact;
	mp_obj_t      read_callback;
	mp_obj_t      write_callback;
} Charact_t;

const mp_obj_type_t Charact_type;


// Get the pointer of characteristic
hap_char_t * Charact_get_ptr(mp_obj_t self_in)
{
	hap_char_t * result = 0;
	Charact_t *self = self_in;
	if (self->base.type == &Charact_type)
	{
		result = self->charact;
	}
	return result;
}


// Call callback on read characteristic
hap_status_t Charact_read_call(hap_char_t *charact)
{
	hap_status_t result = HAP_STATUS_SUCCESS;
	if (charact)
	{
		Charact_t * self;
		ESP_LOGE(TAG, "Read '%s'", hap_char_get_type_uuid(charact));
		self = hap_char_get_priv(charact);
		if (self)
		{
			if (self->charact)
			{
				if (self->read_callback)
				{
					if (mp_obj_is_callable(self->read_callback))
					{
						mp_sched_schedule(self->read_callback, self);
						mp_hal_wake_main_task_from_isr();
					}
				}
			}
		}
	}
	return result;
}

// Call callback on write characteristic
hap_status_t Charact_write_call(hap_char_t *charact, hap_val_t * value)
{
	hap_status_t result = HAP_STATUS_SUCCESS;
	if (charact)
	{
		Charact_t * self;
		ESP_LOGE(TAG, "Write '%s'", hap_char_get_type_uuid(charact));
		self = hap_char_get_priv(charact);
		if (self)
		{
			if (self->charact)
			{
				if (self->write_callback)
				{
					if (mp_obj_is_callable(self->write_callback))
					{
						mp_obj_t val = mp_const_none;
						
						switch(self->type)
						{
						case TYPE_STRING: val = mp_obj_new_str(value->s, strlen(value->s)); break;
						case TYPE_INT   : val = mp_obj_new_int(value->i); break;
						case TYPE_UINT8 : val = mp_obj_new_int(value->u); break;
						case TYPE_UINT32: val = mp_obj_new_int(value->u); break;
						case TYPE_BOOL  : if (value->b) val = mp_const_true; else val = mp_const_false; break;
						case TYPE_FLOAT : val = mp_obj_new_float(value->f); break;
						}
						mp_sched_schedule(self->write_callback, val);
						mp_hal_wake_main_task_from_isr();
					}
				}
			}
		}
	}
	return result;
}


// Constructor method
STATIC mp_obj_t Charact_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args)
{
	mp_obj_t  result = mp_const_none;
	bool paramsOk = true;
	enum 
	{ 
		ARG_uuid,
		ARG_perms,
		ARG_type,
		ARG_value
	};
	// Constructor parameters
	static const mp_arg_t allowed_args[] = 
	{
		{ MP_QSTR_uuid,  MP_ARG_REQUIRED | MP_ARG_OBJ },
		{ MP_QSTR_perms, MP_ARG_REQUIRED | MP_ARG_INT },
		{ MP_QSTR_type,  MP_ARG_REQUIRED | MP_ARG_INT },
		{ MP_QSTR_value, MP_ARG_REQUIRED | MP_ARG_OBJ },
	};
	
	// Parsing parameters
	mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
	mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

	// Check uuid
	if (args[ARG_uuid].u_obj  == mp_const_none || ! mp_obj_is_str(args[ARG_uuid].u_obj))
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Bad uuid"));
		paramsOk = false;
	}
	
	// Check type
	if (args[ARG_type].u_obj  != mp_const_none && args[ARG_value].u_obj  != mp_const_none)
	{
		bool ok = true;
		switch(args[ARG_type].u_int)
		{
		case TYPE_STRING: if (! mp_obj_is_str (args[ARG_value].u_obj))                {ok=false;} break;
		case TYPE_INT   : if (! mp_obj_is_int (args[ARG_value].u_obj))                {ok=false;} break;
		case TYPE_UINT8 : if (! mp_obj_is_int (args[ARG_value].u_obj))                {ok=false;} break;
		case TYPE_UINT32: if (! mp_obj_is_int (args[ARG_value].u_obj))                {ok=false;} break;
		case TYPE_BOOL  : if (! mp_obj_is_bool(args[ARG_value].u_obj))                {ok=false;} break;
		case TYPE_FLOAT : if (! mp_obj_is_type(args[ARG_value].u_obj, &mp_type_float)){ok=false;} break;
		default : ok = false; break;
		}
		
		if (ok == false)
		{
			paramsOk = false;
			mp_raise_TypeError(MP_ERROR_TEXT("Bad value according type"));
		}
	}
	else
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Bad type"));
		paramsOk = false;
	}
	
	// Check permissions
	if (args[ARG_perms].u_obj  == mp_const_none)
	{
		mp_raise_TypeError(MP_ERROR_TEXT("Bad perms"));
		paramsOk = false;
	}
	
	// If all parameters corrects
	if (paramsOk)
	{
		GET_STR_DATA_LEN(args[ARG_uuid].u_obj , uuid, uuid_len);

		// Alloc class instance
		Charact_t *self = m_new_obj_with_finaliser(Charact_t);
		if (self)
		{
			self->charact = 0;
			self->base.type = &Charact_type;
			self->type = args[ARG_type].u_int;
			result = self;
			
			switch(args[ARG_type].u_int)
			{
			case TYPE_STRING:
				{
					GET_STR_DATA_LEN(args[ARG_value].u_obj , value, value_len);
					self->charact = hap_char_string_create((char*)uuid, args[ARG_perms].u_int, (char*) value);
				}
				break;
			case TYPE_INT   : 
				{
					int value = mp_obj_get_int(args[ARG_value].u_obj);
					self->charact = hap_char_int_create((char*)uuid, args[ARG_perms].u_int, value);
				}
				break;
			case TYPE_BOOL  :
				{
					int value = mp_obj_get_int(args[ARG_value].u_obj);
					self->charact = hap_char_bool_create((char*)uuid, args[ARG_perms].u_int, value);
				}
				break;
			case TYPE_FLOAT : 
				{
					float value = mp_obj_get_float(args[ARG_value].u_obj);
					self->charact = hap_char_float_create((char*)uuid, args[ARG_perms].u_int, value);
				}
				break;
			case TYPE_UINT32: 
				{
					int value = mp_obj_get_int(args[ARG_value].u_obj);
					self->charact = hap_char_uint32_create((char*)uuid, args[ARG_perms].u_int, value);
				}
				break;
			case TYPE_UINT8 : 
				{
					int value = mp_obj_get_int(args[ARG_value].u_obj);
					self->charact = hap_char_uint32_create((char*)uuid, args[ARG_perms].u_int, value);
				}
				break;
			}

			if (self->charact)
			{
				hap_char_set_priv(self->charact, self);
			}
		}
	}
	return result;
}


// Delete method
STATIC mp_obj_t Charact_deinit(mp_obj_t self_in)
{
	Charact_t *self = self_in;

	if (self->charact)
	{
		hap_char_delete(self->charact);
	}
	
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(Charact_deinit_obj, Charact_deinit);


// set_unit method
STATIC mp_obj_t Charact_set_unit(mp_obj_t self_in, mp_obj_t unit_in)
{
	Charact_t *self = self_in;
	if (self->charact)
	{
		GET_STR_DATA_LEN(unit_in , unit, unit_len);
		hap_char_add_unit(self->charact, (char*)unit);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Charact_set_unit_obj, Charact_set_unit);


// set_description method
STATIC mp_obj_t Charact_set_description(mp_obj_t self_in, mp_obj_t description_in)
{
	Charact_t *self = self_in;
	if (self->charact)
	{
		GET_STR_DATA_LEN(description_in , description, description_len);
		hap_char_add_description(self->charact, (char*)description);
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Charact_set_description_obj, Charact_set_description);


// set_constraint method
STATIC mp_obj_t Charact_set_constraint(mp_obj_t self_in, mp_obj_t min_in, mp_obj_t max_in)
{
	Charact_t *self = self_in;
	if (self->charact)
	{
		switch(self->type)
		{
		case TYPE_UINT8 : 
		case TYPE_UINT32: 
		case TYPE_INT   : 
			self->min  = mp_obj_get_int(min_in);
			self->max  = mp_obj_get_int(max_in);
			hap_char_int_set_constraints(self->charact, self->min, self->max, self->step);
			break;
		case TYPE_FLOAT : 
			self->min_f  = mp_obj_get_float(min_in);
			self->max_f  = mp_obj_get_float(max_in);
			hap_char_float_set_constraints(self->charact, self->min_f, self->max_f, self->step_f);
			break;
		default:
			mp_raise_TypeError(MP_ERROR_TEXT("Not authorized for this type"));
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(Charact_set_constraint_obj, Charact_set_constraint);


// set_step method
STATIC mp_obj_t Charact_set_step(mp_obj_t self_in, mp_obj_t step_in)
{
	Charact_t *self = self_in;
	if (self->charact)
	{
		switch(self->type)
		{
		case TYPE_UINT8 : 
		case TYPE_UINT32: 
		case TYPE_INT   : 
			self->step  = mp_obj_get_int(step_in);
			hap_char_int_set_constraints(self->charact, self->min, self->max, self->step);
			break;
		case TYPE_FLOAT : 
			self->step_f  = mp_obj_get_float(step_in);
			hap_char_float_set_constraints(self->charact, self->min_f, self->max_f, self->step_f);
			break;
		default:
			mp_raise_TypeError(MP_ERROR_TEXT("Not authorized for this type"));
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Charact_set_step_obj, Charact_set_step);


// set_value method
STATIC mp_obj_t Charact_set_value(mp_obj_t self_in, mp_obj_t value_in)
{
	Charact_t *self = self_in;
	if (self->charact)
	{
		switch(self->type)
		{
		case TYPE_STRING:
			{
				GET_STR_DATA_LEN(value_in , value, value_len);
				hap_val_t new_value;
				new_value.s = (char*) value;
				hap_char_update_val(self->charact, &new_value);
			}
			break;
		case TYPE_INT   : 
			{
				hap_val_t new_value;
				new_value.i = mp_obj_get_int(value_in);
				hap_char_update_val(self->charact, &new_value);
			}
			break;
		case TYPE_BOOL  :
			{
				hap_val_t new_value;
				
				if (mp_obj_get_int(value_in) == 1)
				{
					new_value.b = true;
				}
				else
				{
					new_value.b = false;
				}
				hap_char_update_val(self->charact, &new_value);
			}
			break;
		case TYPE_FLOAT : 
			{
				hap_val_t new_value;
				new_value.f = mp_obj_get_float(value_in);
				hap_char_update_val(self->charact, &new_value);
			}
			break;
		case TYPE_UINT32: 
			{
				hap_val_t new_value;
				new_value.u = mp_obj_get_int(value_in);
				hap_char_update_val(self->charact, &new_value);
			}
			break;
		case TYPE_UINT8 : 
			{
				hap_val_t new_value;
				new_value.u = mp_obj_get_int(value_in);
				hap_char_update_val(self->charact, &new_value);
			}
			break;
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Charact_set_value_obj, Charact_set_value);


// get_value method
STATIC mp_obj_t Charact_get_value(mp_obj_t self_in)
{
	Charact_t *self = self_in;
	mp_obj_t result = mp_const_none;
	if (self->charact)
	{
		switch(self->type)
		{
		case TYPE_STRING:
			{
				const hap_val_t * value = hap_char_get_val(self->charact);
				if (value)
				{
					if (value->s)
					{
						result = mp_obj_new_str(value->s, strlen(value->s));
					}
				}
			}
			break;
		case TYPE_INT   : 
			{
				const hap_val_t * value = hap_char_get_val(self->charact);
				if (value)
				{
					result = mp_obj_new_int(value->i);
				}
			}
			break;
		case TYPE_BOOL  :
			{
				const hap_val_t * value = hap_char_get_val(self->charact);
				if (value)
				{
					if (value->b)
					{
						result = mp_const_true;
					}
					else
					{
						result = mp_const_false;
					}
				}
			}
			break;
		case TYPE_FLOAT : 
			{
				const hap_val_t * value = hap_char_get_val(self->charact);
				if (value)
				{
					result = mp_obj_new_float(value->f);
				}
			}
			break;
		case TYPE_UINT32: 
			{
				const hap_val_t * value = hap_char_get_val(self->charact);
				if (value)
				{
					result = mp_obj_new_int(value->u);
				}
			}
			break;
		case TYPE_UINT8 : 
			{
				const hap_val_t * value = hap_char_get_val(self->charact);
				if (value)
				{
					result = mp_obj_new_int(value->u);
				}
			}
			break;
		}
	}
	return result;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(Charact_get_value_obj, Charact_get_value);


// set_read_callback method
STATIC mp_obj_t Charact_set_read_callback(mp_obj_t self_in, mp_obj_t read_callback_in)
{
	Charact_t *self = self_in;

	if (self->charact)
	{
		if (read_callback_in != mp_const_none && !mp_obj_is_callable(read_callback_in)) 
		{
			mp_raise_ValueError(MP_ERROR_TEXT("invalid read_callback"));
		}
		else
		{
			self->read_callback = read_callback_in;
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Charact_set_read_callback_obj, Charact_set_read_callback);


// set_write_callback method
STATIC mp_obj_t Charact_set_write_callback(mp_obj_t self_in, mp_obj_t write_callback_in)
{
	Charact_t *self = self_in;

	if (self->charact)
	{
		if (write_callback_in != mp_const_none && !mp_obj_is_callable(write_callback_in)) 
		{
			mp_raise_ValueError(MP_ERROR_TEXT("invalid write_callback"));
		}
		else
		{
			self->write_callback = write_callback_in;
		}
	}
	return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(Charact_set_write_callback_obj, Charact_set_write_callback);


// print method
STATIC void Charact_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) 
{
	ESP_LOGE(TAG, "Charact_print");
}


// Methods
STATIC const mp_rom_map_elem_t Charact_locals_dict_table[] = 
{
	// Delete method
	{ MP_ROM_QSTR(MP_QSTR___del__),            MP_ROM_PTR(&Charact_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_deinit),             MP_ROM_PTR(&Charact_deinit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_unit),           MP_ROM_PTR(&Charact_set_unit_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_description),    MP_ROM_PTR(&Charact_set_description_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_constraint),     MP_ROM_PTR(&Charact_set_constraint_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_step),           MP_ROM_PTR(&Charact_set_step_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_value),          MP_ROM_PTR(&Charact_set_value_obj) },
	{ MP_ROM_QSTR(MP_QSTR_get_value),          MP_ROM_PTR(&Charact_get_value_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_read_callback),  MP_ROM_PTR(&Charact_set_read_callback_obj) },
	{ MP_ROM_QSTR(MP_QSTR_set_write_callback), MP_ROM_PTR(&Charact_set_write_callback_obj) },
};
STATIC MP_DEFINE_CONST_DICT(Charact_locals_dict, Charact_locals_dict_table);

// Class definition
const mp_obj_type_t Charact_type = 
{
	{ &mp_type_type },
	.name        = MP_QSTR_Charact,
	.print       = Charact_print,
	.make_new    = Charact_make_new,
	.locals_dict = (mp_obj_t)&Charact_locals_dict,
};

