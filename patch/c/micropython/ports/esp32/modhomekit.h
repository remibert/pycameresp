/* Distributed under MIT License
Copyright (c) 2021 Remi BERTHOLET */
#ifndef modhomekit_h_included
#define modhomekit_h_included

#include <esp_log.h>
#include <hap.h>
#include <hap_apple_chars.h>
#include "py/runtime.h"
#include "py/objstr.h"
#include "py/gc.h"
#include "py/mpstate.h"
#include "py/stackctrl.h"
#include "mphalport.h"
#include "string.h"


// Get the pointer of characteristic
hap_char_t * Charact_get_ptr(mp_obj_t self_in);

// Call callback on read characteristic
hap_status_t Charact_read_call(hap_char_t *charact);

// Call callback on write characteristic
hap_status_t Charact_write_call(hap_char_t *charact, hap_val_t * value);

// Get the pointer of server
hap_serv_t * Server_get_ptr(mp_obj_t self_in);

// Get the pointer of accessory
hap_acc_t * Accessory_get_ptr(mp_obj_t self_in);

const mp_obj_type_t Charact_type;
const mp_obj_type_t Server_type;
const mp_obj_type_t Accessory_type;
const mp_obj_type_t Homekit_type;
void hap_keystore_erase_all_data();
#endif
