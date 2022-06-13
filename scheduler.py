import traceback
import datetime
import win32com.client

def createTask(task):
    createTask(    
        task["folder"],
        task["taskname"],
        task["start"],
        task["end"],
        task["exe"],
        task["args"])

def createTask(folder, taskname, tstart, tend, xtool, xargs):
    try:
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        try:
            rootfolder = scheduler.GetFolder(folder)
        except:
            rootfolder = scheduler.GetFolder("\\")
            rootfolder.CreateFolder(folder)
            rootfolder = scheduler.GetFolder(folder)

        # Create task
        taskdef = scheduler.NewTask(0)
        taskdef.RegistrationInfo.Description = 'StreamRec Task'
        #task_def.Principal.LogonType = 3
        taskdef.Settings.Enabled = True
        taskdef.Settings.StopIfGoingOnBatteries = False
        taskdef.Settings.StartWhenAvailable = True
        taskdef.Settings.Hidden = False
        taskdef.Settings.DeleteExpiredTaskAfter = "PT2H" 

        # Create trigger
        TASK_TRIGGER_TIME = 1
        trigger = taskdef.Triggers.Create(TASK_TRIGGER_TIME)
        trigger.Id = taskname
        trigger.StartBoundary = tstart.isoformat()
        trigger.EndBoundary = tend.isoformat()
        dm = int ((tend - tstart).seconds / 60)
        trigger.ExecutionTimeLimit = f'PT{dm // 60}H{dm % 60}M'

        # Create action
        TASK_ACTION_EXEC = 0
        action = taskdef.Actions.Create(TASK_ACTION_EXEC)
        action.ID = 'Record'
        action.Path = xtool
        action.Arguments = xargs

        # Register task. If task already exists, it will be updated
        TASK_CREATE_OR_UPDATE = 6
        TASK_LOGON_NONE = 0
        rootfolder.RegisterTaskDefinition(
            taskname,
            taskdef,
            TASK_CREATE_OR_UPDATE,
            '',  # No user
            '',  # No password
            TASK_LOGON_NONE)
    except:
        traceback.print_exc()

