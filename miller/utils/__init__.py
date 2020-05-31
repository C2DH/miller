import re
import datetime
import logging

logger = logging.getLogger(__name__)


def data_paths(headers, prefix='data__', delimiter="__", list_delimiter='|'):
    """
    rebuild the structure of data JSON onject based on __
    concatenation of headers
    """
    return [(
        x,
        x.split(list_delimiter)[0].split(delimiter),
        x.split(list_delimiter)[-1] == 'list'
    ) for x in filter(
        lambda x: isinstance(x, str) and x.startswith(prefix), headers
    )]


def nested_set(
    data, path, value, as_list=False,
    datetime_suffix=('start_date', 'end_date',)
):
    """
    directly edit data
    """
    for key in path[:-1]:
        data = data.setdefault(key, {})
    if data is None:
        raise ValueError('key "{}" is not a valid dict! Check "{}"'.format(
            key,
            u'__'.join(path)
        ))
    if not as_list:
        if isinstance(value, bool):
            data[path[-1]] = value
        elif not value:
            data[path[-1]] = ''
        elif path[-1] in datetime_suffix:
            # print('nested:', path[-1], value)
            if isinstance(value, str):
                m = re.search(
                    r'(^Date\(?)?(\d{4})[,\-](\d{1,2})[,\-](\d{1,2})\)?',
                    value
                )
                if m is not None:
                    if m.group(1) is not None:
                        # this makes use of Date(1917,4,21) google spreadsheet
                        # dateformat.
                        # also note that month 4 is not April but is May (wtf)
                        logger.info('parsing date field: {}, value: {}'.format(
                            path[-1],
                            value
                        ))
                        data[path[-1]] = datetime.datetime(
                            year=int(m.group(2)),
                            month=int(m.group(3)) + 1,
                            day=int(m.group(4))
                        ).isoformat()
                    elif m.group(2) is not None:
                        # 0 padded values, 1917-05-21
                        data[path[-1]] = datetime.datetime.strptime('-'.join((
                            m.group(2),
                            m.group(3),
                            m.group(4),
                        )), '%Y-%m-%d').isoformat()
                elif value:
                    data[path[-1]] = xldate_to_datetime(
                        float(value)
                    ).isoformat()
            else:
                data[path[-1]] = xldate_to_datetime(
                    float(value)
                ).isoformat()
        else:
            data[path[-1]] = value
    else:
        # if as_list: it is a list, comma separated ;)
        data[path[-1]] = list(map(lambda x: x.strip(), filter(
            None,
            [] if not value else value.split(',')
        )))
    return data


def get_data_from_dict(obj, datetime_suffix=('start_date', 'end_date',)):
    # headers contains a dict_keys object,
    # e.g.(['data__title__fr_FR', 'data__title__en_GB'])
    headers = obj.keys()
    # data paths transform headers into possible paths, e.g.
    # 'data__title__fr_FR' becomes a tuple key, path, is_list, e.g.
    # ('data__title__fr_FR', ['data', 'title', 'fr_FR'], False)
    dp = data_paths(headers=headers)
    data = {}
    # for i, path, is_list in dp:
    #   nested_set(data, path, {})
    # at the end of this loop, data paths will be merged:
    # e.g: list ['data__title__fr_FR', 'data__title__en_GB'] becomes
    # {'data': {'title': {'fr_FR': 'un joli title', 'en_GB': 'A nicer title'}}}
    for key, path, is_list in dp:
        nested_set(
            data=data, path=path, value=obj[key],
            as_list=is_list, datetime_suffix=datetime_suffix
        )
    return data


def xldate_to_datetime(xldate, datemode=0):
    # datemode: 0 for 1900-based, 1 for 1904-based
    epoch = datetime.datetime(1899, 12, 30)
    excel_date = datetime.timedelta(days=xldate + 1462 * datemode)
    return epoch + excel_date
