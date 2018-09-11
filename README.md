CLI to scan a text file (or stdin when providing `-` as file) for URLs and other patterns to open them in a browser.

This tool is meant to be used with `todo.txt` and in particular [topydo] as demonstrated in `topydo_sample.txt`.

	usage: open_urls.py [-h] [--finders [{tasks,urls} [{tasks,urls} ...]]]
	                    [--cmd CMD] [--dry-run]
	                    FILE
	
	Scans file for patterns and opens found URLs.
	
	positional arguments:
	  FILE                  file to analyze
	
	optional arguments:
	  -h, --help            show this help message and exit
	  --finders [{tasks,urls} [{tasks,urls} ...]]
	                        only given set of finders
	  --cmd CMD             command to execute for each URL
	  --dry-run             print all commands to be executed

## custom patterns

Patterns are processed by "finders" that produce a set of URLs from a given string.
This example can is part of `open_urls.py` and can be modified or duplicated according to your specific needs:

	# maps tasks such as T1234 -> https://tasks/1234
	REGEX_TASK = re.compile(r"""\bT(\d+)\b""")
	def find_tasks(line):
		return set('https://tasks/' + m.group(1) for m in REGEX_TASK.finditer(line))
		
	ALL_FINDERS['tasks'] = find_tasks



[topydo]: https://github.com/bram85/topydo