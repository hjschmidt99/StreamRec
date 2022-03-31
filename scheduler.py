import traceback
import datetime
import win32com.client

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
        taskdef.Settings.taskDefinition.Settings.StartWhenAvailable = True
        taskdef.Settings.taskDefinition.Settings.Hidden = False
        taskdef.Settings.taskDefinition.Settings.DeleteExpiredTaskAfter = "PT2H" 

        # Create trigger
        TASK_TRIGGER_TIME = 1
        trigger = taskdef.Triggers.Create(TASK_TRIGGER_TIME)
        trigger.Id = taskname
        trigger.StartBoundary = tstart.isoformat()
        trigger.EndBoundary = tend.isoformat()
        dt = datetime.datetime.strftime(tend - tstart, "%HH%mM")
        trigger.ExecutionTimeLimit = f'PT{dt}'

        # Create action
        TASK_ACTION_EXEC = 0
        action = taskdef.Actions.Create(TASK_ACTION_EXEC)
        action.ID = 'DO NOTHING'
        action.Path = xtool
        action.Arguments = xargs

        # Register tas. If task already exists, it will be updated
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

