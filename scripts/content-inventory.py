#!/usr/bin/env python3
"""Count published content separately from reviewed long-form features.

Word counts describe body copy only. They do not establish originality,
accuracy, indexing or ranking. Unparsed legacy markup is never called thin.
"""
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_site import scan_articles
from business_depth import article_body_span
from directory_index import VERIFIED


def plain(markup):
    markup = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', markup, flags=re.S | re.I)
    return ' '.join(unescape(re.sub(r'<[^>]+>', ' ', markup)).split())


def inventory():
    features_path = ROOT / 'data/profile-features.json'
    features = json.loads(features_path.read_text()) if features_path.exists() else {}
    articles = scan_articles(str(ROOT))
    rows, errors = [], []
    errors.extend(f'{slug}: feature has no verified business record' for slug in sorted(set(features)-set(VERIFIED)))
    hashes = defaultdict(list)
    for article in articles:
        slug = article['slug']
        markup = (ROOT / 'news' / slug / 'index.html').read_text()
        span = article_body_span(markup)
        text = plain(markup[span[0]:span[1]]) if span else None
        count = len(text.split()) if text is not None else None
        if text:
            hashes[hashlib.sha256(text.encode()).hexdigest()].append(slug)
        rows.append({'kind': 'article', 'slug': slug, 'body_words': count,
                     'review_status': 'unparsed' if span is None else 'length_only',
                     'source_pages': None})
    seen_paragraphs = {}
    for slug in sorted(VERIFIED):
        feature = features.get(slug)
        count, sources = None, set()
        if feature:
            paragraphs = []
            for section in feature['sections']:
                source = section.get('source_url')
                if source:
                    if urlsplit(source).scheme != 'https' or not urlsplit(source).netloc:
                        errors.append(f'{slug}: feature source is not a valid HTTPS URL')
                    sources.add(source)
                for paragraph in section['paragraphs']:
                    normalized = plain(paragraph).casefold()
                    if normalized in seen_paragraphs:
                        errors.append(f'{slug}: repeated feature paragraph from {seen_paragraphs[normalized]}')
                    seen_paragraphs[normalized] = slug
                    paragraphs.append(paragraph)
            count = sum(len(p.split()) for p in paragraphs)
            if count < 600:
                errors.append(f'{slug}: reviewed feature is below the 600-word publication standard')
            if len(sources) < 3:
                errors.append(f'{slug}: feature needs at least three reviewed source pages')
            if not feature.get('checked'):
                errors.append(f'{slug}: missing feature research date')
            for link in feature['related']:
                route = link['url']
                if not route.startswith('/') or not (ROOT / route.lstrip('/') / 'index.html').exists():
                    errors.append(f'{slug}: missing local feature link {route}')
        rows.append({'kind': 'business', 'slug': slug, 'body_words': count,
                     'review_status': 'individual_feature' if feature else 'legacy_not_assessed',
                     'source_pages': len(sources) if feature else None})
    summary = {
        'targets': {'articles': 5000, 'businesses': 5000},
        'published': {'articles': len(articles), 'businesses': len(VERIFIED)},
        'remaining_to_count_targets': {'articles': max(0, 5000-len(articles)),
                                       'businesses': max(0, 5000-len(VERIFIED))},
        'article_length_only': {
            'at_least_600_words': sum(r['kind']=='article' and r['body_words'] is not None and r['body_words']>=600 for r in rows),
            'below_600_words': sum(r['kind']=='article' and r['body_words'] is not None and r['body_words']<600 for r in rows),
            'unparsed': sum(r['kind']=='article' and r['body_words'] is None for r in rows)},
        'individually_reviewed_business_features': len(features),
        'identical_article_body_groups': [slugs for slugs in hashes.values() if len(slugs)>1],
        'feature_validation_errors': errors,
        'limitations': ['Archive totals include legacy coverage requiring intent and evidence review.',
                       'Word counts are not quality scores; shared directory guidance is excluded from feature counts.',
                       'Different wording can still duplicate intent; manual editorial review remains required.']}
    output = ROOT / 'editorial'
    (output / 'content-inventory.json').write_text(json.dumps(summary, indent=2)+'\n')
    with (output / 'content-inventory.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['kind','slug','body_words','review_status','source_pages'])
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(summary, indent=2))
    return not errors


if __name__ == '__main__':
    raise SystemExit(0 if inventory() else 1)
