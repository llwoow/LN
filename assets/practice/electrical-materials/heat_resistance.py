#!/usr/bin/env python3
"""An explicitly hypothetical steady one-dimensional slab-conduction case.

No measured material property or physical experiment is claimed.
"""
import json


def thermal_resistance(thickness_m, conductivity_W_mK, area_m2):
    if thickness_m <= 0 or conductivity_W_mK <= 0 or area_m2 <= 0:
        raise ValueError('Geometry and conductivity must be positive')
    return thickness_m / (conductivity_W_mK * area_m2)


def example():
    thickness_m = 0.004
    area_m2 = 0.01
    conductivity_W_mK = 0.2
    heat_flow_W = 8.0
    resistance_K_W = thermal_resistance(thickness_m, conductivity_W_mK, area_m2)
    delta_temperature_K = heat_flow_W * resistance_K_W
    assert abs(resistance_K_W - 2.0) < 1e-12
    assert abs(delta_temperature_K - 16.0) < 1e-12
    assert abs(thermal_resistance(2 * thickness_m, conductivity_W_mK, area_m2) - 4.0) < 1e-12
    return {
        'case': 'hypothetical 1D steady slab, constant conductivity, no contacts',
        'thermal_resistance_K_per_W': resistance_K_W,
        'temperature_difference_K': delta_temperature_K,
        'double_thickness_resistance_K_per_W': 4.0
    }


if __name__ == '__main__':
    print(json.dumps(example(), ensure_ascii=False, indent=2))
