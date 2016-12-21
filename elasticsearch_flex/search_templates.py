import json
import logging
import re
import os

from six import text_type

logger = logging.getLogger(__name__)


class SearchTemplate(object):
    def __init__(self, index, filepath):
        self._index = index
        self.template = self._prerender(filepath)

    def register(self):
        # TODO
        logger.info('Registering template <%s>', self._index)

    def unregister(self):
        pass

    def sync(self):
        pass

    def _prerender(self, filepath):
        file_abspath = os.path.abspath(filepath)
        file_dir = os.path.dirname(file_abspath)
        with open(filepath, 'r') as fp:
            content = json.load(fp)

        # Recurse and look for a #[filename] pattern and load that file.
        def interpolate(dat):
            if type(dat) is dict:
                return {k: interpolate(v) for k, v in dat.items()}
            elif type(dat) is list:
                return [interpolate(x) for x in dat]
            elif type(dat) is text_type:
                matches = re.match(r'#\[(.+)\]', dat)
                if matches is not None:
                    script_name = matches.group(1)
                    script_file = os.path.join(file_dir, '{}.java'.format(script_name))
                    with open(script_file, 'r') as fp:
                        script = fp.read()
                        # XXX: Very cheap Java code "minification".
                        # It looks for spaces and tab marks in the beginning
                        # and end of the string, and replaces them with a single
                        # space.
                        # This is not robust and will fail for multi-line
                        # strings which want to preserve the spaces, however
                        # in our use case, we probably won't need that.
                        # In any case, this can use a rewrite.
                        return re.sub(r'^[ \t]+|\s+$', ' ', script, flags=re.M)
            return dat

        prerendered = interpolate(content)
        return json.dumps(prerendered)
