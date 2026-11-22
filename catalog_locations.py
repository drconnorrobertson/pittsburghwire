"""Keep published street addresses separate from sourced service coverage."""
from urllib.parse import urlsplit

def location_errors(row):
 errors=[];address=row.get('address','').strip()
 if row.get('address_kind')=='service_area':
  if address:errors.append('service-area record must not imply a street address')
  if not row.get('area_served','').strip():errors.append('service-area record requires published coverage')
  source=row.get('area_served_source','');parsed=urlsplit(source)
  official=urlsplit(row.get('official_research',{}).get('url',''))
  if parsed.scheme!='https' or not parsed.hostname or parsed.hostname!=official.hostname:errors.append('service-area coverage requires an official-source URL')
  if row.get('official_research',{}).get('status')!='corroborated':errors.append('service-area identity must be corroborated')
 elif not address:errors.append('empty address')
 return errors

def display_location(row):
 if row.get('address_kind')=='service_area':return 'Service area: '+row['area_served']
 return row.get('address','Pittsburgh area')
