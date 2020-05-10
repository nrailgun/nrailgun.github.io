import os
import re

yaml = '''---
layout: post
title: "%s"
categories: %s
date: 2020-05-10 00:00:00
---
'''

for root, dir, files in os.walk('./_posts/'):
	new_root = root.lower().replace(' ', '-')

	for file in files:
		if file == 'goals.md':
			continue
		if re.match(r'^\d+-\d+-\d+.+', file):
			continue
		if not file.endswith('.md'):
			continue
		new_file = '2020-05-10-%s' % file.lower().replace(' ', '-')
		category = os.path.basename(new_root)

		x = None
		with open(os.path.join(root, file), 'r') as of:
			cont = of.read()
			y = yaml % (file[:-3], category)
			x = '%s\n%s' % (y, cont)
		with open(os.path.join(root, file), 'w') as of:
			of.write(x)

		os.rename(os.path.join(root, file), os.path.join(root, new_file))
	os.rename(root, new_root)
