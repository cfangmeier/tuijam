def sec_to_min_sec(sec_tot):
    s = int(sec_tot or 0)
    return s // 60, s % 60
