
import json

d_p = json.load(open('franquias/data.json', encoding='utf-8-sig'))
d_n = json.load(open('novo projeto/franquias/data.json', encoding='utf-8-sig'))

def get_store(lst, sid):
    for x in lst:
        if str(x.get('storeId')) == str(sid):
            return x
    return {}

rb_id = '19762'
print('=== RIO BRANCO (19762) ===')
for w in ['17 a 23', '24 a 30', '31 a 06', '07 a 13']:
    p = get_store(d_p['adt']['weeks'][w], rb_id)
    n = get_store(d_n['adt']['weeks'][w], rb_id)
    print(f'Week {w}:')
    print('  PROD:', p)
    print('  NOVO:', n)

p_ac = get_store(d_p['adt']['acumulado'], rb_id)
n_ac = get_store(d_n['adt']['acumulado'], rb_id)
print('Acumulado:')
print('  PROD:', p_ac)
print('  NOVO:', n_ac)
