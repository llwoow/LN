"""Recheck published aggregates only, not the household survey or its microdata."""
import json
components=[23327,6908,3435,7644]
mean=41314;median=34707
assert sum(components)==mean
print(json.dumps({'year':2024,'published_components_yuan':components,'sum_yuan':sum(components),
 'median_divided_by_mean_percent':100*median/mean,
 'limits':'The ratio compares two income statistics. It is not a share of persons or households; this does not reproduce survey sampling.'},indent=2))
