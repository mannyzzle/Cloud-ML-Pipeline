import sys
import os

# Ensure the backend module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db_connection
from app.tle_processor import fetch_tle_data, compute_orbital_params

def update_satellite_data():
    """
    Fetches TLE data, processes it, and updates the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    satellites = fetch_tle_data()
    print(f"📡 Fetched {len(satellites)} satellites for processing.")

    for sat in satellites[:5]:  # Test with first 5 satellites
        params = compute_orbital_params(sat["line1"], sat["line2"])
        if params:
            cursor.execute("""
                INSERT INTO satellites (
                    name, tle_line1, tle_line2, norad_number, intl_designator, ephemeris_type,
                    inclination, eccentricity, period, perigee, apogee, epoch, raan, arg_perigee,
                    mean_motion, semi_major_axis, velocity, orbit_type, bstar, rev_num
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (name) DO UPDATE SET
                    tle_line1 = EXCLUDED.tle_line1,
                    tle_line2 = EXCLUDED.tle_line2,
                    norad_number = EXCLUDED.norad_number,
                    intl_designator = EXCLUDED.intl_designator,
                    ephemeris_type = EXCLUDED.ephemeris_type,
                    inclination = EXCLUDED.inclination,
                    eccentricity = EXCLUDED.eccentricity,
                    period = EXCLUDED.period,
                    perigee = EXCLUDED.perigee,
                    apogee = EXCLUDED.apogee,
                    epoch = EXCLUDED.epoch,
                    raan = EXCLUDED.raan,
                    arg_perigee = EXCLUDED.arg_perigee,
                    mean_motion = EXCLUDED.mean_motion,
                    semi_major_axis = EXCLUDED.semi_major_axis,
                    velocity = EXCLUDED.velocity,
                    orbit_type = EXCLUDED.orbit_type,
                    bstar = EXCLUDED.bstar,
                    rev_num = EXCLUDED.rev_num;
            """, (
                sat["name"], sat["line1"], sat["line2"], params["norad_number"], params["intl_designator"],
                params["ephemeris_type"], params["inclination"], params["eccentricity"], params["period"],
                params["perigee"], params["apogee"], params["epoch"], params["raan"], params["arg_perigee"],
                params["mean_motion"], params["semi_major_axis"], params["velocity"], params["orbit_type"],
                params["bstar"], params["rev_num"]
            ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Satellite data updated successfully!")

if __name__ == "__main__":
    update_satellite_data()
