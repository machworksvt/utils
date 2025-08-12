import openvsp as vsp
import Scripts.tools as tl

# Canonical constant map + alias list per item
_constant_definitions = {
    # --- Length Units ---
    "LEN_MM":     { "value": vsp.LEN_MM,     "aliases": ["mm", "millimeter"] },
    "LEN_CM":     { "value": vsp.LEN_CM,     "aliases": ["cm", "centimeter"] },
    "LEN_M":      { "value": vsp.LEN_M,      "aliases": ["m", "meter", "metre"] },
    "LEN_IN":     { "value": vsp.LEN_IN,     "aliases": ["in", "inch", "\""] },
    "LEN_FT":     { "value": vsp.LEN_FT,     "aliases": ["ft", "feet", "'"] },
    "LEN_YD":     { "value": vsp.LEN_YD,     "aliases": ["yd", "yard"] },
    "LEN_UNITLESS": { "value": vsp.LEN_UNITLESS, "aliases": ["unitless"] },

    # --- Velocity Units ---
    "V_UNIT_M_S": {
        "value": vsp.V_UNIT_M_S,
        "aliases": ["m/s", "meters per second"]
    },
    "V_UNIT_FT_S": {
        "value": vsp.V_UNIT_FT_S,
        "aliases": ["ft/s", "feet per second"]
    },
    "V_UNIT_MPH": {
        "value": vsp.V_UNIT_MPH,
        "aliases": ["mph", "mile per hour"]
    },
    "V_UNIT_KM_HR": {
        "value": vsp.V_UNIT_KM_HR,
        "aliases": ["km/hr", "km/h", "kilometer per hour"]
    },
    "V_UNIT_KEAS": {
        "value": vsp.V_UNIT_KEAS,
        "aliases": ["keas", "knots equivalent airspeed"]
    },
    "V_UNIT_KTAS": {
        "value": vsp.V_UNIT_KTAS,
        "aliases": ["ktas", "knots", "knots true airspeed"]
    },
    "V_UNIT_MACH": {
        "value": vsp.V_UNIT_MACH,
        "aliases": ["mach"]
    },

    # --- Pressure Units ---
    "PRES_UNIT_PSF": {
        "value": vsp.PRES_UNIT_PSF,
        "aliases": ["psf", "pounds per square foot"]
    },
    "PRES_UNIT_PSI": {
        "value": vsp.PRES_UNIT_PSI,
        "aliases": ["psi", "pounds per square inch"]
    },
    "PRES_UNIT_BA": {
        "value": vsp.PRES_UNIT_BA,
        "aliases": ["ba", "barye"]
    },
    "PRES_UNIT_PA": {
        "value": vsp.PRES_UNIT_PA,
        "aliases": ["pa", "pascal"]
    },
    "PRES_UNIT_KPA": {
        "value": vsp.PRES_UNIT_KPA,
        "aliases": ["kpa", "kilopascal"]
    },
    "PRES_UNIT_MPA": {
        "value": vsp.PRES_UNIT_MPA,
        "aliases": ["mpa", "megapascal"]
    },
    "PRES_UNIT_INCHHG": {
        "value": vsp.PRES_UNIT_INCHHG,
        "aliases": ["inchhg", "inHg", "inch of mercury"]
    },
    "PRES_UNIT_MMHG": {
        "value": vsp.PRES_UNIT_MMHG,
        "aliases": ["mmhg", "millimeter of mercury"]
    },
    "PRES_UNIT_MMH20": {
        "value": vsp.PRES_UNIT_MMH20,
        "aliases": ["mmh2o", "millimeter of water"]
    },
    "PRES_UNIT_MB": {
        "value": vsp.PRES_UNIT_MB,
        "aliases": ["mb", "millibar"]
    },
    "PRES_UNIT_ATM": {
        "value": vsp.PRES_UNIT_ATM,
        "aliases": ["atm", "atmosphere"]
    },

    # --- Temperature Units ---
    "TEMP_UNIT_K": {
        "value": vsp.TEMP_UNIT_K,
        "aliases": ["k", "kelvin"]
    },
    "TEMP_UNIT_C": {
        "value": vsp.TEMP_UNIT_C,
        "aliases": ["c", "celsius", "°c"]
    },
    "TEMP_UNIT_F": {
        "value": vsp.TEMP_UNIT_F,
        "aliases": ["f", "fahrenheit", "°f"]
    },
    "TEMP_UNIT_R": {
        "value": vsp.TEMP_UNIT_R,
        "aliases": ["r", "rankine"]
    },

        # --- Mass Units ---
    "MASS_UNIT_G": {
        "value": vsp.MASS_UNIT_G,
        "aliases": ["g", "gram"]
    },
    "MASS_UNIT_KG": {
        "value": vsp.MASS_UNIT_KG,
        "aliases": ["kg", "kilogram"]
    },
    "MASS_UNIT_TONNE": {
        "value": vsp.MASS_UNIT_TONNE,
        "aliases": ["tonne", "metric ton"]
    },
    "MASS_UNIT_LBM": {
        "value": vsp.MASS_UNIT_LBM,
        "aliases": ["lbm", "pound-mass", "lb"]
    },
    "MASS_UNIT_SLUG": {
        "value": vsp.MASS_UNIT_SLUG,
        "aliases": ["slug"]
    },

    # --- Density Units ---
    "RHO_UNIT_SLUG_FT3": {
        "value": vsp.RHO_UNIT_SLUG_FT3,
        "aliases": ["slug/ft^3", "slug per cubic foot"]
    },
    "RHO_UNIT_G_CM3": {
        "value": vsp.RHO_UNIT_G_CM3,
        "aliases": ["g/cm^3", "gram per cubic centimeter"]
    },
    "RHO_UNIT_KG_M3": {
        "value": vsp.RHO_UNIT_KG_M3,
        "aliases": ["kg/m^3", "kilogram per cubic meter"]
    },
    "RHO_UNIT_TONNE_MM3": {
        "value": vsp.RHO_UNIT_TONNE_MM3,
        "aliases": ["tonne/mm^3", "tonne per cubic millimeter"]
    },
    "RHO_UNIT_LBM_FT3": {
        "value": vsp.RHO_UNIT_LBM_FT3,
        "aliases": ["lbm/ft^3", "pound-mass per cubic foot"]
    },
    "RHO_UNIT_LBFSEC2_IN4": {
        "value": vsp.RHO_UNIT_LBFSEC2_IN4,
        "aliases": ["lbf·s²/in⁴", "pound-force-second squared per inch to the fourth"]
    },
    "RHO_UNIT_LBM_IN3": {
        "value": vsp.RHO_UNIT_LBM_IN3,
        "aliases": ["lbm/in^3", "pound-mass per cubic inch"]
    },
    # Atmosphere Models
    "ATMOS_TYPE_HERRINGTON_1966": {
        "value": vsp.ATMOS_TYPE_HERRINGTON_1966,
        "aliases": ["herrington", "1966"]
    },
    "ATMOS_TYPE_MANUAL_P_R": {
        "value": vsp.ATMOS_TYPE_MANUAL_P_R,
        "aliases": ["manual-pr"]
    },
    "ATMOS_TYPE_MANUAL_P_T": {
        "value": vsp.ATMOS_TYPE_MANUAL_P_T,
        "aliases": ["manual-pt"]
    },
    "ATMOS_TYPE_MANUAL_RE_L": {
        "value": vsp.ATMOS_TYPE_MANUAL_RE_L,
        "aliases": ["manual-rel"]
    },
    "ATMOS_TYPE_MANUAL_R_T": {
        "value": vsp.ATMOS_TYPE_MANUAL_R_T,
        "aliases": ["manual-rt"]
    },
    "ATMOS_TYPE_US_STANDARD_1976": {
        "value": vsp.ATMOS_TYPE_US_STANDARD_1976,
        "aliases": ["us_standard", "us standard", "1976"]
    },

    # --- Other Constants (as provided previously) ---
    "CF_LAM_BLASIUS": {
        "value": vsp.CF_LAM_BLASIUS,
        "aliases": ["blasius"]
    },
    "CF_TURB_POWER_LAW": {
        "value": vsp.CF_TURB_POWER_LAW_BLASIUS,
        "aliases": ["powerlaw"]
    },
    "CF_TURB_IMPLICIT_KARMAN_SCHOENHERR": {
        "value": vsp.CF_TURB_IMPLICIT_KARMAN_SCHOENHERR,
        "aliases": ["karman"]
    },
    "FF_W_DATCOM": {
        "value": vsp.FF_W_DATCOM,
        "aliases": ["datcom"]
    },
    "EXCRESCENCE_COUNT": {
        "value": vsp.EXCRESCENCE_COUNT,
        "aliases": ["count"]
    },
    "EXCRESCENCE_CD": {
        "value": vsp.EXCRESCENCE_CD,
        "aliases": ["cd"]
    },
    "EXCRESCENCE_PERCENT_GEOM": {
        "value": vsp.EXCRESCENCE_PERCENT_GEOM,
        "aliases": ["percent"]
    },
    "AR_WSECT_DRIVER": {
        "value": vsp.AR_WSECT_DRIVER,
        "aliases": ["aspect", "aspectratio", "ar"]
    },
    "SPAN_WSECT_DRIVER": {
        "value": vsp.SPAN_WSECT_DRIVER,
        "aliases": ["span"]
    },
    "AREA_WSECT_DRIVER": {
        "value": vsp.AREA_WSECT_DRIVER,
        "aliases": ["area"]
    },
    "TAPER_WSECT_DRIVER": {
        "value": vsp.TAPER_WSECT_DRIVER,
        "aliases": ["taper", "taper ratio"]
    },
    "AVEC_WSECT_DRIVER": {
        "value": vsp.AVEC_WSECT_DRIVER,
        "aliases": ["average chord", "avg chord", "ave chord", "avgc"]
    },
    "ROOTC_WSECT_DRIVER": {
        "value": vsp.ROOTC_WSECT_DRIVER,
        "aliases": ["root chord", "rootc"]
    },
    "TIPC_WSECT_DRIVER": {
        "value": vsp.TIPC_WSECT_DRIVER,
        "aliases": ["tip chord", "tipc"]
    },
    "SECSWEEP_WSECT_DRIVER": {
        "value": vsp.SECSWEEP_WSECT_DRIVER,
        "aliases": ["sweep", "section sweep", "secsweep"]
    }
}


_constant_lookup = {}
for canonical_name, entry in _constant_definitions.items():
    _constant_lookup[canonical_name.upper()] = entry["value"]
    for alias in entry.get("aliases", []):
        _constant_lookup[alias.strip().lower()] = entry["value"]

def get_vsp_constant(name):
    key = name.strip()

    # Try exact match
    if key in _constant_lookup:
        return _constant_lookup[key]

    # Try upper/lower casing
    if key.upper() in _constant_lookup:
        return _constant_lookup[key.upper()]
    if key.lower() in _constant_lookup:
        return _constant_lookup[key.lower()]

    # Fallback to getattr if not found
    return _fallback_lookup(key)


def _fallback_lookup(key):
    try:
        val = getattr(vsp, key.upper())
        tl.sprint(f"VSP Constant '{key}' not found in dictionary — using getattr fallback", -2)
        return val
    except AttributeError:
        tl.sprint(f"Unknown constant: '{key}'", -1, lead_func=True)
        return None