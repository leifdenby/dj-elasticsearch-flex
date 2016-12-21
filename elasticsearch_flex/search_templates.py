import json
import re

from six import string_types


class SearchTemplate(object):
    def __init__(self, index, filepath):
        self._index = index
        self._prerender(filepath)

    def register(self):
        pass

    def unregister(self):
        pass

    def sync(self):
        pass

    def _prerender(self, filepath):
        with open(filepath, 'r') as fp:
            content = json.load(fp)

        # Recurse and look for a #[filename] pattern and load that file.
        def interpolate(dat):
            if type(dat) is dict:
                return {k: interpolate(v) for k, v in dat.items()}
            elif type(dat) is list:
                return [interpolate(x) for x in dat]
            elif type(dat) is string_types:
                # Do interpolation
                matches = re.match(r'#\[(<scriptname>.+)\]', dat)
                if matches is not None:
                    script_name = matches.group('scriptname')
                    script_file = 'search_templates/{}.java'.format(script_name)
                    with open(script_file, 'r') as fp:
                        return fp.read()
            return dat

        prerendered = interpolate(content)
        return json.dumps(prerendered)
