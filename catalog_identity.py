"""Business identity is a name and location, never a citation URL alone."""
import re

def identity_key(row):
    name=re.sub(r'[^a-z0-9]','',row.get('name','').casefold())
    address=row.get('address','').casefold()
    replacements={'street':'st','avenue':'ave','road':'rd','boulevard':'blvd','drive':'dr','lane':'ln','suite':'ste','pennsylvania':'pa'}
    address=re.sub(r'\b(street|avenue|road|boulevard|drive|lane|suite|pennsylvania)\b',lambda m:replacements[m[0]],address)
    address=re.sub(r'(\b\d{5})-\d{4}\b',r'\1',address)
    location=re.sub(r'[^a-z0-9]','',address)
    # Service-area providers have no street identity; do not collapse providers
    # merely because they serve the same community.
    return (name,location)if name and location else None

def duplicate_identities(data):
    seen={};duplicates=[]
    for slug,row in data.items():
        key=identity_key(row)
        if key is not None:
            if key in seen:duplicates.append((seen[key],slug))
            else:seen[key]=slug
    return duplicates
