import collections


def group_all_tags(idx, group):
    all_tags = collections.OrderedDict()
    # all_tags["ALL"] = len(idx["group"][group])
    for tag in sorted(idx["tags"].keys()):
        length = len(idx["tags"][tag] & idx["group"][group])
        if length > 0:
            all_tags[tag] = length
    return all_tags
