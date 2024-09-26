/*
 * Copyright (C) 2024 The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

#include <cstring>

#define _REALLY_INCLUDE_SYS__SYSTEM_PROPERTIES_H_
#include <sys/_system_properties.h>
#include <android-base/properties.h>

#include "property_service.h"
#include "vendor_init.h"

#include "init_sm8550.h"

using android::base::GetProperty;
using std::string;

// List of partitions to override props
static const string source_partitions[] = {
    "", "bootimage.", "odm.", "product.", "system.",
    "system_dlkm.", "system_ext.", "vendor.", "vendor_dlkm."
};

void property_override(char const prop[], char const value[]) {
    auto pi = (prop_info*) __system_property_find(prop);

    if (pi != nullptr) {
        __system_property_update(pi, value, std::strlen(value));
    } else {
        __system_property_add(prop, std::strlen(prop), value, std::strlen(value));
    }
}

void set_build_prop(const string &prop, const string &value) {
    property_override(prop.c_str(), value.c_str());
}

void set_ro_build_prop(const string &prop, const string &value) {
    for (const string &source : source_partitions) {
        property_override(("ro.product." + source + prop).c_str(), value.c_str());
    }
}

void vendor_load_properties() {
    // Detect variant and override properties
    string model = GetProperty("ro.boot.em.model", "");
    string device, name;

    for (const auto &current_variant : all_variants) {
        if (model == current_variant.model) {
            device = current_variant.codename;
            name = current_variant.codename + (current_variant.region == "Global" ? "xxx" : "zhx");
            break;
        }
    }

    // Override device specific props
    set_ro_build_prop("device", device);
    set_ro_build_prop("model", model);
    set_ro_build_prop("name", name);
    set_build_prop("ro.build.product", device);
}
