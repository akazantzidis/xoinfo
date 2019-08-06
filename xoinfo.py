#!/usr/bin/env python3

from xolib import xo, XoError, XoApiError, XoTimeoutError
from texttable import Texttable
import argparse
import getpass
import pprint
import sys
import itertools

def connect(xo_server,username):
    password = getpass.getpass('Enter your XenOrchestra password:')
#    xo_session = xo('ws://' + xo_server,email=username,password='blabla')
    xo_session = xo('ws://' + xo_server,email=username,password=password)
    try:        
        return xo_session
    except XoError:
        print('Wrong password?')
        raise

def get_objects_with_type(xo_instance,obj_type=None):
    object_dict = None
    try:
        object_dict = xo_instance.call('xo.getAllObjects')
    except XoTimeoutError:
        print('xo-server did not respond within 20 seconds.')
        raise
    except XoApiError:
        print('Fix your arguments.')
        raise
    if obj_type is not None:
        result_dict={k: v for k,v  in object_dict.items() if v ['type']==obj_type}
    else:
        result_dict = object_dict
    return result_dict

def return_pools(pooldict):
    podict={}    
    for uuid, name_label in pooldict.items():
         name = pooldict[uuid]['name_label']
         podict[uuid]= name
    for uuid,name in podict.items():
        print(name)

def return_vms_with_tags(vmtaglist,pool):
    vm_tag_list=[]
    for uuid, vm_data in vm_dict.items():
        for tag in vmtaglist:
            if pool is not '':
                if tag in vm_data['tags'] and pool in vm_data['$pool']:
                    vm_tag_list.append(uuid)
            else:
                if tag in vm_data['tags']:
                    vm_tag_list.append(uuid)

    return vm_tag_list

def return_running_vm(pool):
    vm_run_list = []
    for uuid, vm_data in vm_dict.items():
        if pool is not '':
            if 'Running' in vm_data['power_state'] and pool in vm_data['$pool']:
                vm_run_list.append(uuid)

        else:
            if 'Running' in vm_data['power_state']:
                vm_run_list.append(uuid)

    return vm_run_list

def return_allvm(vm_dict, pool_uuid, resp):
    vm_uuid_list=[]
    vm_name_list=[]
    for vm_uuid, vm_data in vm_dict.items():
        if pool_uuid is not '':
            vm = vm_dict[vm_uuid]['$pool']
            if vm == pool_uuid:
                vm_uuid_list.append(vm_uuid)
            else:
                pass
        else:
            vm_uuid_list.append(vm_uuid)
    if resp is False:
        for id in vm_uuid_list:
            vmname = vm_dict[id]['name_label']
            vm_name_list.append(vmname)
        return vm_name_list
    else:
        return vm_uuid_list

def get_pool_uuid_by_name_label(pool_dict,name):
    for uuid ,name_label in pool_dict.items():
        if pool_dict[uuid]['name_label'] == name:
            return uuid

def get_vm_uuid_by_name_label(vm_dict,name):
    for uuid ,name_label in pool_dict.items():
        if name_label == name:
            return uuid

def create_table(tablelist):
    table= Texttable()
    for item in tablelist:
        table.add_row([item[0],item[1]])
    ftable = table.draw()
    return ftable

def return_addresses(vm_uuid):
    dict_addr = {}
    if vm_dict[vm_uuid]['addresses'] is not None:
            for address_idx, address in vm_dict[vm_uuid]['addresses'].items():
                if 'ipv6' in address_idx:
                    pass
                else:
                    dict_addr[address_idx[:-3]] = address
    else:
        dict_addr = {}
    return dict_addr

def return_vif_net(vif_list):
    vif_net_dict = {}
    for item in vif_list:
        vif_id = vif_dict[item]['device']
        vif_network_uuid = vif_dict[item]['$network']
        vif_net_name = net_dict[vif_network_uuid]['name_label']
        vif_net_dict[vif_id] = vif_net_name
    return vif_net_dict

def return_vm_nic_ip(vmlist):
    vif_net_dict = {}
    vif_addr_dict = {}
    return_dict = {}
    return_list = []

    for uuid in vmlist:
        vm_name = str(vm_dict[uuid]['name_label'])
        vm_addresses_dict = return_addresses(uuid)
        vm_inf_net_dict = return_vif_net(vm_dict[uuid]['VIFs'])
        c = 0
        if len(vm_addresses_dict.keys()) == len(vm_inf_net_dict.keys()):
            for vifindex, netvalue in sorted(vm_inf_net_dict.items()):
                vif_net_dict[c] = netvalue
                c+=1
            c = 0
            for  addressindex, address in sorted(vm_addresses_dict.items()):
                vif_addr_dict[c] = address
                c+=1
            return_dict[vm_name] = dict(zip(vif_addr_dict.values(), vif_net_dict.values()))
        else:
            laddrkeys = len(vif_addr_dict.keys())
            if len(vif_addr_dict.keys()) < len(vm_inf_net_dict.keys()):
                while laddrkeys != len(vm_inf_net_dict.keys()):
                    vif_addr_dict[laddrkeys] = ('No ip address')
                    laddrkeys+=1
            for vifindex, netvalue in sorted(vm_inf_net_dict.items()):
                vif_net_dict[c] = netvalue
                c+=1
            c = 0
            for  addressindex, address in sorted(vm_addresses_dict.items()):
                vif_addr_dict[c] = address
                c+=1
            return_dict[vm_name] = dict(zip(vif_addr_dict.values(), vif_net_dict.values()))

        vm = vm_name
        ips = '\n'.join(map(str,vif_addr_dict.values()))
        net = '\n'.join(map(str,vif_net_dict.values()))
        return_list.append([vm,ips,net])
        vif_net_dict = {}
        vif_addr_dict = {}    
    
    return return_list

def create_vmtable(list):
    table= Texttable()
    for item in list:
        table.add_row([item])
    vmtable = table.draw()
    return vmtable

def create_vmiptable(list):
    table= Texttable()
    for item in list:
        table.add_row([item[0],item[1]])
    vmiptable = table.draw()
    return vmiptable

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--list-pools',action='store_true')
    parser.add_argument('-u','--username')
    parser.add_argument('-x','--xo-server')
    parser.add_argument('-p','--from-pool')
    parser.add_argument('-vm','--vm',action='store_true')
    parser.add_argument('-ip','--ip',action='store_true')
    parser.add_argument('-d','--debug',action='store_true')
    parser.add_argument('-i','--vmuuid')
    parser.add_argument('-tags' , nargs='*')
    parser.add_argument('--running',action='store_true')
    args= parser.parse_args()

    if args.username is not None and args.xo_server is not None:
        pass
    else:
        print('Not enough arguments provided')
        exit(1)
    
    xo_session=connect(args.xo_server,args.username)
    vm_dict= get_objects_with_type(xo_session,obj_type='VM')
    pool_dict = get_objects_with_type(xo_session,obj_type='pool')
    vif_dict = get_objects_with_type(xo_session,obj_type='VIF')
    net_dict = get_objects_with_type(xo_session,obj_type='network')


    if args.list_pools:
        return_pools(pool_dict)
        exit()

    if args.from_pool is None and args.debug is True and args.vmuuid is not None:
        vm = args.vmuuid
        print(return_vm_nic_ip(vm))

    if args.from_pool is None and args.vm is False and args.running is True:
        pool_uuid = ''
        vms = return_running_vm(pool_uuid)
        print(create_table(return_vm_nic_ip(vms)))

    elif args.from_pool is not None and args.vm is False and args.running is True:
        pool_uuid = get_pool_uuid_by_name_label(pool_dict,args.from_pool)
        vms = return_running_vm(pool_uuid)
        print(create_table(return_vm_nic_ip(vms)))

    elif args.from_pool is not None and args.vm is False and args.tags is not None:
        pool_uuid = get_pool_uuid_by_name_label(pool_dict,args.from_pool)
        vms = return_vms_with_tags(args.tags, pool_uuid)
        print(create_table(return_vm_nic_ip(vms)))

    elif args.from_pool is None and args.vm is False and args.tags is not None:
        pool_uuid = ''
        vms = return_vms_with_tags(args.tags, pool_uuid)
        print(create_table(return_vm_nic_ip(vms)))

    elif args.from_pool is not None and args.vm is False:
        resp = True
        pool_uuid = get_pool_uuid_by_name_label(pool_dict,args.from_pool)
        vms = return_allvm(vm_dict, pool_uuid,resp )
        print(create_table(return_vm_nic_ip(vms)))

    elif args.from_pool is None and args.vm is False:
        resp = True
        pool_uuid = ''
        vms = return_allvm(vm_dict, pool_uuid,resp)
        print(create_table(return_vm_nic_ip(vms)))

    elif args.from_pool is not None and args.vm is True and args.ip is False:
        resp = False
        pool_uuid = get_pool_uuid_by_name_label(pool_dict,args.from_pool)
        vms = return_allvm(vm_dict, pool_uuid,resp)
        print(create_vmtable(vms))

    elif args.from_pool is None and args.vm is True and args.ip is False:
        resp = False
        pool_uuid = ''
        vms = return_allvm(vm_dict, pool_uuid,resp)
        print(create_vmtable(vms))

    elif args.from_pool is None and args.vm is True and args.ip is True:
        resp = True
        pool_uuid = ''
        vms = return_allvm(vm_dict, pool_uuid,resp)
        print(create_vmiptable((return_vm_nic_ip(vms))))

    elif args.from_pool is not None and args.vm is True and args.ip is True:
        resp = True
        pool_uuid = get_pool_uuid_by_name_label(pool_dict,args.from_pool)
        vms = return_allvm(vm_dict, pool_uuid,resp)
        print(create_vmiptable((return_vm_nic_ip(vms))))