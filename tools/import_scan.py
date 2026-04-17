import sys
import pkgutil
import importlib

sys.path.insert(0, r'c:\Users\Eneri Junior\qagent')
errors = []
modules = []
for finder, name, ispkg in pkgutil.walk_packages(['src']):
    mod_name = 'src.' + name
    modules.append(mod_name)
    try:
        importlib.import_module(mod_name)
    except Exception as e:
        errors.append((mod_name, repr(e)))

print('modules_count=', len(modules))
print('errors_count=', len(errors))
for mod, err in errors:
    print(mod, '->', err)

if not errors:
    print('All modules imported successfully.')
