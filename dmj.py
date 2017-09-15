# coding: utf-8
import random
import socket
import requests
import xml.dom.minidom
import struct
import simplejson
from const import BCommand


class DMJBot(object):
    def __init__(self, room_id, u_id=0):
        self.room_id = room_id
        self.api_room_detail_url = 'https://api.live.bilibili.com/api/player?id=cid:{}'.format(room_id)
        self.dm_host = None
        self.socket_client = self._set_up()
        self._uid = u_id or int(100000000000000.0 + 200000000000000.0 * random.random())
        self.magic = 16
        self.ver = 1
        self.into_room = 7
        self.package_type = 1
        self.max_data_length = 65495

    def _set_up(self):
        room_detail_xml_string = self._http_get_request(self.api_room_detail_url)
        xml_string = ('<root>' + room_detail_xml_string.strip() + '</root>').encode('utf-8')
        root = xml.dom.minidom.parseString(xml_string).documentElement
        dm_server = root.getElementsByTagName('dm_server')
        self.dm_host = dm_server[0].firstChild.data

        # tcp_socket return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.dm_host, 2243))
        print self.dm_host
        return s

    def _http_get_request(self, url):
        s = requests.session()
        response = s.get(url)
        return response.text

    def _pack_socket_data(self, data_length, data):
        _data = data.encode('utf-8')
        _send_bytes = struct.pack('!IHHII', data_length, self.magic, self.ver, self.into_room, self.package_type)
        return _send_bytes + _data

    def _parse_data(self, json_data):
        if json_data['cmd'] == BCommand.DANMU_MSG:
            pass
        elif json_data['cmd'] == BCommand.SEND_GIFT:
            pass
        elif json_data['cmd'] == BCommand.WELCOME:
            pass

    def _start(self):
        # 是JSON 前面要补16字节数据
        _dmj_data = simplejson.dumps({
            "roomid": self.room_id,
            "uid": self._uid,
        }, separators=(',', ':'))
        total_length = 16 + len(_dmj_data)
        data = self._pack_socket_data(total_length, _dmj_data)
        self.socket_client.send(data)

        # 会断是因为心跳问题，需要30秒内发送心跳
        # 这里先接收确认进入房间的信息
        x = self.socket_client.recv(16)
        while True:
            data = self.socket_client.recv(self.max_data_length)
            data_length, magic, ver, message_type, package_type = struct.unpack('!IHHII', data[0:16])
            if data_length == 16:
                print data_length
                continue
            try:
                json = data[16:].decode('utf-8')
                json_data = simplejson.loads(json)
            except simplejson.JSONDecodeError:
                print 'wrong+++++++++++'
                print data[16:].decode('utf-8')
                print 'wrong end+++++++++++'
            except UnicodeDecodeError:
                print 'UNICODE wrong+++++++++++'
                print data[16:]
                print 'UNICODE wrong end+++++++++++'


if __name__ == '__main__':
    room_id = 79558
    # 010101
    # room_id = 989474
    # 魔王127直播间
    # room_id = 35137
    dmj = DMJBot(room_id)
    dmj._start()
