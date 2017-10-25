#!/usr/bin/env python

import rospy
import os
import logging
import yaml
import json
from motors.configs import *
import webui.srv as srv
from subprocess import Popen

logger = logging.getLogger('hr.webui.bug_controller')

def write_yaml(filename, data):
    # delete existing config
    try:
        os.remove(filename)
    except OSError:
        pass

    dir = os.path.dirname(filename)
    if not os.path.exists(dir):
        os.makedirs(dir)

    f = open(filename, 'w')
    f.write(yaml.safe_dump(data, encoding='utf-8', allow_unicode=True))
    f.close()

def load_params(param_file, namespace):
    Popen("rosparam load " + param_file + " " + namespace, shell=True)


def kill_node(node):
    Popen("rosnode kill " + node, shell=True)


class MotorsController:
    def __init__(self):
        rospy.init_node('motors_controller')
        self.assemblies = rospy.get_param('/assemblies')
        rospy.Service('~update_motors', srv.UpdateMotors, self.update_motors)
        rospy.Service('~update_expressions', srv.UpdateExpressions, self.update_expressions)
        rospy.Service('~save_expressions', srv.UpdateMotors, self.save_expressions)
        rospy.Service('~save_animations', srv.UpdateMotors, self.save_animations)
        self.config_root = rospy.get_param('/robots_config_dir')
        rospy.spin()

    def update_motors(self, req):
        configs = Configs(self.assemblies)
        robot_name = req.robot_name
        configs.parseMotors(json.loads(req.motors))
        for k, assembly  in configs.assemblies.iteritems():
            if len(assembly['dynamixel']) > 0:
                file_name = os.path.join(assembly['assembly'], "dynamixel.yaml")
                write_yaml(file_name, assembly['dynamixel'])
                load_params(file_name, "/{}/safe".format(robot_name))
            if len(assembly['motors']) > 0:
                file_name = os.path.join(assembly['assembly'], "motors.yaml")
                write_yaml(file_name, {'motors': assembly['motors']})
                load_params(file_name, "/{}".format(robot_name))
            if len(assembly['pololu']) > 0:
                for board, config in assembly['pololu'].iteritems():
                    file_name = os.path.join(assembly['assembly'], board + ".yaml")
                    write_yaml(file_name, config)
                    kill_node("/{}/pololu_{}".format(robot_name, board))
        kill_node("/{}/pau2motors".format(robot_name))
        kill_node("/{}/basic_head_api".format(robot_name))
        return srv.UpdateMotorsResponse(True)

    def save_expressions(self, req):
        robot_name = req.robot_name
        motors = rospy.get_param('/{}/motors'.format(robot_name))
        # Using same service type as saving motors
        data = json.loads(req.motors)
        config_files = {}
        for a in self.assemblies:
            config_files[os.path.basename(a)] = {'assembly':a, 'data':{'expressions': []}}
        # Find assembly by first motor name
        for expression in data['expressions']:
            try:
                motor = expression.values()[0].keys()[0]
                assembly = motors[motor]['assembly']
                config_files[assembly]['data']['expressions'].append(expression)
            except Exception as e:
                rospy.logerr(e)
                raise e

        for cfg in config_files.values():
            if len(cfg['data']['expressions']) == 0:
                # Expressions file is unecessary for the assembly
                try:
                    os.remove(os.path.join(cfg['assembly'], 'expressions.yaml'))
                except OSError:
                    pass
            write_yaml(os.path.join(cfg['assembly'], 'expressions.yaml'), cfg['data'])
        return srv.UpdateMotorsResponse(True)

    def save_animations(self, req):
        robot_name = req.robot_name
        motors = rospy.get_param('/{}/motors'.format(robot_name))
        # Using same service type as saving motors
        data = json.loads(req.motors)
        config_files = {}
        for a in self.assemblies:
            config_files[os.path.basename(a)] = {'assembly':a, 'data':{'animations': []}}
        # Find assembly by first motor name
        for animation in data['animations']:
            try:
                # Rather complicated structure of animations file
                motor = animation.values()[0][0]['motors'].keys()[0]
                assembly = motors[motor]['assembly']
                config_files[assembly]['data']['animations'].append(animation)
            except IndexError:
                continue
            except Exception as e:
                rospy.logerr(e)
                rospy.logerr(animation.values()[0])
                raise e
        for cfg in config_files.values():
            if len(cfg['data']['animations']) == 0:
                # Expressions file is unecessary for the assembly
                try:
                    os.remove(os.path.join(cfg['assembly'], 'animations.yaml'))
                except OSError:
                    pass
            write_yaml(os.path.join(cfg['assembly'], 'animations.yaml'), cfg['data'])
        return srv.UpdateMotorsResponse(True)


    def update_expressions(self, req):
        robot_name = req.robot_name
        expressions = os.path.join(self.config_root, robot_name, "expressions.yaml")
        load_params(expressions, "/{}".format(robot_name))
        animations = os.path.join(self.config_root, robot_name, "animations.yaml")
        load_params(animations, "/{}".format(robot_name))
        kill_node("/{}/basic_head_api".format(robot_name))
        return srv.UpdateExpressionsResponse(True)


if __name__ == '__main__':
    MotorsController()
