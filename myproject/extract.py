#!/usr/bin/env python
# encoding: utf-8

# 该文件用于提取网页的正文部分，针对通用型网页

import chardet
import re
import lxml.etree


def transform_coding(text):
    if not isinstance(text, unicode):
        text_encode = chardet.detect(text)['encoding']
        try:
            text = text.decode(text_encode if text_encode else 'utf8')
        except Exception as e:
            pass
    return text


def remove_js_css(content):
    """ remove the the javascript and the stylesheet and the comment content (<script>....</script> and <style>....</style> <!-- xxx -->) """
    r = re.compile(r'''<script.*?</script>''', re.I|re.M|re.S)
    s = r.sub('', content)
    r = re.compile(r'''<style.*?</style>''', re.I|re.M|re.S)
    s = r.sub('', s)
    r = re.compile(r'''<!--.*?-->''', re.I|re.M|re.S)
    s = r.sub('', s)
    r = re.compile(r'''<meta.*?>''', re.I|re.M|re.S)
    s = r.sub('', s)
    r = re.compile(r'''<ins.*?</ins>''', re.I|re.M|re.S)
    s = r.sub('', s)
    return s


def remove_empty_line(content):
    """remove multi space """
    r = re.compile(r'''^\s+$''', re.M|re.S)
    s = r.sub('', content)
    r = re.compile(r'''\n+''', re.M|re.S)
    s = r.sub('\n', s)
    return s


def remove_any_tag(s):
    s = re.sub(r'''<[^>]+>''', '', s)
    return s.strip()


def remove_any_tag_but_a(s):
    text = re.findall(r'''<a[^r][^>]*>(.*?)</a>''', s, re.I|re.M|re.S)
    text_b = remove_any_tag(s)
    return len(''.join(text)), len(text_b)


def remove_image(s, n=50):
    image = 'a' * n
    r = re.compile(r'''<img.*?>''', re.I|re.M|re.S)
    s = r.sub(image, s)
    return s


def remove_video(s, n=1000):
    video = 'a' * n
    r = re.compile(r'''<embed.*?>''', re.I|re.M|re.S)
    s = r.sub(video, s)
    return s


def sum_max(values):
    cur_max = values[0]
    glo_max = -999999
    left, right = 0, 0
    for index, value in enumerate(values):
        cur_max += value
        if (cur_max > glo_max):
            glo_max = cur_max
            right = index
        elif (cur_max < 0):
            cur_max = 0

    for i in range(right, -1, -1):
        glo_max -= values[i]
        if abs(glo_max) < 0.00001:
            left = i
            break

    return left, right+1


def method_1(content, k=1):
    if not content:
        return None, None, None, None
    
    tmp = content.split('\n')
    group_value = []
    
    for i in range(0, len(tmp), k):
        group = '\n'.join(tmp[i:i+k])
        group = remove_image(group)
        group = remove_video(group)
        text_a, text_b = remove_any_tag_but_a(group)
        temp = (text_b - text_a) - 8
        group_value.append(temp)

    left, right = sum_max(group_value)
    return left, right, len('\n'.join(tmp[:left])), len('\n'.join(tmp[:right]))


def extract(content):
    content = remove_empty_line(remove_js_css(content))
    left, right, x, y = method_1(content)

    content = '\n'.join(content.split('\n')[left:right])
    content = transform_coding(content)

    r = re.findall(r'''<p.*?>(.*?)</p>''', content, re.I|re.M|re.S)
    if not r:
        return None, None, None

    try:
        index = content.index('发布时间：'.decode('utf8'))
        s = e = index + 5
        while True:
            if content[e].isdigit() or content[e] in [' ', '-', ':', '.', '年'.decode('utf8'), '月'.decode('utf8'), '日'.decode('utf8')]:
                e += 1
            else:
                publishedtime = content[s:e].strip()
                break
    except Exception as e:
        publishedtime = None

    r = [lxml.etree.HTML('<p>'+i+'</p>').xpath('//p')[0].xpath('string(.)') for i in r]
    summary = r[0]
    main_body = '\n'.join(r)
    return summary, main_body, publishedtime




if __name__ == '__main__':
    f = open('1.html', 'r')
    text = f.read()
    
    title = re.findall(r'''<title.*?>(.*?)</title>''', text, re.I|re.M|re.S)
    print title[0], len(title)

    # content = extract(text)
    # r = re.compile(r'<.*?>', re.I|re.M|re.S)
    # s = r.sub('', content)

    abstract, main_body, publishedtime = extract(text)
    print '---' * 30
    print abstract
    print '---' * 30
    print main_body
    print '---' * 30
    print publishedtime
    f.close()

