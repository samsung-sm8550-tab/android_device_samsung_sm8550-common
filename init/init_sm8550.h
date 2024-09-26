/*
 * Copyright (C) 2024 The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef INIT_SM8550_H
#define INIT_SM8550_H

#include <string>

enum device_variant {
    VARIANT_S9110 = 0,
    VARIANT_S911B,
    VARIANT_S9160,
    VARIANT_S916B,
    VARIANT_S9180,
    VARIANT_S918B,
    VARIANT_MAX
};

typedef struct {
    std::string model;
    std::string codename;
    std::string region;
} variant;

static const variant all_variants[VARIANT_MAX] = {
    {"SM-S9110", "dm1q", "CN"},
    {"SM-S911B", "dm1q", "Global"},
    {"SM-S9160", "dm2q", "CN"},
    {"SM-S916B", "dm2q", "Global"},
    {"SM-S9180", "dm3q", "CN"},
    {"SM-S918B", "dm3q", "Global"}
};

#endif // INIT_SM8550_H
