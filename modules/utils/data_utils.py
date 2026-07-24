def encrypt_data(data, key):
    """
    根据key作凯撒加密, key长度小于data，因此key循环使用
    """
    return "".join([chr(ord(data[i]) ^ ord(key[i % len(key)])) for i in range(len(data))])

def decrypt_data(data, key):
    """
    根据key作凯撒解密, key长度小于data，因此key循环使用
    """
    return "".join([chr(ord(data[i]) ^ ord(key[i % len(key)])) for i in range(len(data))])

def return_now_activate_pipeline(use_config):
    """
    返回给定config激活了的 pipeline 的 任务列表和任务开关列表 

    返回 TASK_PIPELINE 和 TASK_ONOFF 列表

    task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
    
    """
    activate_pipeline_ind = use_config.userconfigdict["TASK_ORDER_GROUP"]["ACTIVATE_IND"]
    all_pipelines = use_config.userconfigdict["TASK_ORDER_GROUP"]["ALL_PIPELINES"]
    assert activate_pipeline_ind is not None
    assert all_pipelines is not None
    # ---
    activate_pipeline = all_pipelines[activate_pipeline_ind]["TASK_PIPELINE"]
    task_onoff = all_pipelines[activate_pipeline_ind]["TASK_ONOFF"]
    assert activate_pipeline is not None
    assert task_onoff is not None

    if len(activate_pipeline) < len(task_onoff):
        # 截断 task_onoff
        del task_onoff[len(activate_pipeline):]
    if len(activate_pipeline) > len(task_onoff):
        # 补充 task_onoff 为 False
        for _ in range(len(activate_pipeline) - len(task_onoff)):
            task_onoff.append(False)

    return activate_pipeline, task_onoff, all_pipelines, activate_pipeline_ind