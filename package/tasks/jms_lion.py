import os

from .base import BaseTask, TaskType


__all__ = ['JmsLionTask']


class JmsLionTask(BaseTask):
    NAME = '堡垒机 lion 组件信息'
    TYPE = TaskType.JUMPSERVER

    def __init__(self):
        super().__init__()
        self.jms_config = None
        self.mysql_client = None

    @staticmethod
    def get_do_params():
        return ['jms_config', 'mysql_client']

    def _get_windows_online_session_count(self):
        connect_type = ('WT', )
        protocol = ('rdp', 'vnc')
        sql = "select count(*) from terminal_session " \
              "where is_finished=%s and login_from in %s " \
              "and protocol in %s"
        self.mysql_client.execute(sql, (False, connect_type, protocol))
        sql_result = self.mysql_client.fetchone()[0]
        return sql_result

    def _get_lion_replay_file_size(self):
        volume_dir = self.jms_config.get('VOLUME_DIR')
        log_path = os.path.join(volume_dir, 'lion', 'data', 'replays')
        command = 'cd %s;du -sh' % log_path
        resp, ok = self.do_command(command)
        if not ok:
            self.abnormal_number += 1
            self.task_result.append((resp, True))
        else:
            online_count = self._get_windows_online_session_count()
            var = resp.split()[0]
            item_resp = '当前录像文件总大小: %s，' \
                        '使用 lion 组件的在线会话数为 %s ' \
                        '(如果堡垒机长时间无人使用且此值过大，请检查是否存在遗留录像)' % (var, online_count)
            self.task_result.append((item_resp, False))

    def do(self):
        if self._ssh_client is None:
            raise Exception('任务执行前需要先注册一个SSH Client')
        self._get_lion_replay_file_size()
        return self.task_result