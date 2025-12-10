-- Сиды для таблицы law_sources: официальные RSS-ленты publication.pravo.gov.ru

INSERT INTO law_sources (name, base_url, type, parser, config, is_active) VALUES
-- Общая лента
('pravo_rss_all',
 'http://publication.pravo.gov.ru/api/rss?pageSize=200',
 'rss',
 'pravo_gov_rss',
 '{"scope":"all"}',
 1),

-- Блоки по типам органов власти
('pravo_rss_president',
 'http://publication.pravo.gov.ru/api/rss?block=president&pageSize=200',
 'rss',
 'pravo_gov_rss',
 '{"block":"president"}',
 1),

('pravo_rss_government',
 'http://publication.pravo.gov.ru/api/rss?block=government&pageSize=200',
 'rss',
 'pravo_gov_rss',
 '{"block":"government"}',
 1),

('pravo_rss_council_1',
 'http://publication.pravo.gov.ru/api/rss?block=council_1&pageSize=200',
 'rss',
 'pravo_gov_rss',
 '{"block":"council_1"}',
 1),

('pravo_rss_council_2',
 'http://publication.pravo.gov.ru/api/rss?block=council_2&pageSize=200',
 'rss',
 'pravo_gov_rss',
 '{"block":"council_2"}',
 1),

('pravo_rss_federal_authorities',
 'http://publication.pravo.gov.ru/api/rss?block=federal_authorities&pageSize=200',
 'rss',
 'pravo_gov_rss',
 '{"block":"federal_authorities"}',
 1),

('pravo_rss_court',
 'http://publication.pravo.gov.ru/api/rss?block=court&pageSize=200',
 'rss',
 'pravo_gov_rss',
 '{"block":"court"}',
 1),

('pravo_rss_international',
 'http://publication.pravo.gov.ru/api/rss?block=international&pageSize=200',
 'rss',
 'pravo_gov_rss',
 '{"block":"international"}',
 1),

-- Ленты по конкретным органам (org = GUID)
('pravo_rss_org_1049e10d',
 'http://publication.pravo.gov.ru/api/rss?org=1049e10d-0133-4ef6-95ae-a487c0e7f653&pageSize=10',
 'rss',
 'pravo_gov_rss',
 '{"org":"1049e10d-0133-4ef6-95ae-a487c0e7f653"}',
 1),

('pravo_rss_org_ff850c93',
 'http://publication.pravo.gov.ru/api/rss?org=ff850c93-e869-42ec-9547-a63dad38c204&pageSize=10',
 'rss',
 'pravo_gov_rss',
 '{"org":"ff850c93-e869-42ec-9547-a63dad38c204"}',
 1),

('pravo_rss_org_af104b65',
 'http://publication.pravo.gov.ru/api/rss?org=af104b65-fa9b-4976-a75e-445ef35bcb28&pageSize=10',
 'rss',
 'pravo_gov_rss',
 '{"org":"af104b65-fa9b-4976-a75e-445ef35bcb28"}',
 1),

('pravo_rss_org_f69ec43f',
 'http://publication.pravo.gov.ru/api/rss?org=f69ec43f-3fa5-4611-a286-52acdcc77334&pageSize=10',
 'rss',
 'pravo_gov_rss',
 '{"org":"f69ec43f-3fa5-4611-a286-52acdcc77334"}',
 1),

('pravo_rss_org_2c4929b0',
 'http://publication.pravo.gov.ru/api/rss?org=2c4929b0-9323-4541-9705-76185b9e284b&pageSize=10',
 'rss',
 'pravo_gov_rss',
 '{"org":"2c4929b0-9323-4541-9705-76185b9e284b"}',
 1),

('pravo_rss_org_d959e5e5',
 'http://publication.pravo.gov.ru/api/rss?org=d959e5e5-b261-43cf-8529-eb19cc364d69&pageSize=10',
 'rss',
 'pravo_gov_rss',
 '{"org":"d959e5e5-b261-43cf-8529-eb19cc364d69"}',
 1),

('pravo_rss_org_e39d1726',
 'http://publication.pravo.gov.ru/api/rss?org=e39d1726-9473-4a70-916e-16ce7b183d0f&pageSize=10',
 'rss',
 'pravo_gov_rss',
 '{"org":"e39d1726-9473-4a70-916e-16ce7b183d0f"}',
 1);

