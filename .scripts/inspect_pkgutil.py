import pkgutil, sys
print('pkgutil file:', getattr(pkgutil, '__file__', None))
print('has find_loader:', hasattr(pkgutil, 'find_loader'))
print('find_loader attr:', getattr(pkgutil, 'find_loader', None))
print('dir contains find_loader:', 'find_loader' in dir(pkgutil))
print('sys.path sample:', sys.path[:5])
print('pkgutil module repr:', pkgutil)
