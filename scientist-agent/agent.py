# import datetime
# from zoneinfo import ZoneInfo
# from google.adk.agents import Agent
from google.adk.agents.llm_agent import Agent
# from google.adk.code_executors.built_in_code_executor import BuiltInCodeExecutor
# from google.adk.tools import built_in_code_execution
# from google.adk.tools import google_search
from google.adk.tools import FunctionTool, ToolContext, load_artifacts
from google.genai import types
import os
import pysd
import pandas as pd
import numpy as np

def list_models(domain: str) -> dict:
    """Lists all system dynamics models in the given domain.
    
    Args:
        domain: The domain to list models from. This will be interpreted as a subdirectory of "source/models/" in the local file system.
        example: "Epidemic"
    
    Returns:
        dict: A dictionary containing the `status` (success/failure), and `files` whose value is an array of strings which are paths to model files (either vensim or xmile) inside `source/models/<domain>`.
        example: {"status": "success", "files": ["SI.mdl", "SIR.xmile", "SEIR.mdl"]}
    """
    print("Inside list_models.......")
    import os
    model_files = []
    for root, dirs, files in os.walk("source/models/" + domain):
        for file in files:
            if file.endswith(".mdl") or file.endswith(".xmile"):
                model_files.append(os.path.join(root, file))
    return {
        "status": "success",
        "files": model_files
    }

def read_model_file(model_path: str) -> dict:
    """Reads a system dynamics model from the given local path and saves it as an artifact.
    
    Args:
        model_path: The path to the model file.
    
    Returns:
        dict: A dictionary containing the status (success/failure), artifact_name and message.
    """
    print("Inside read_model_file.......")
    with open(model_path, "r") as f:
        model = f.read()
        return {
            "status": "success",
            "model": model
        }
        
def write_model_file(model_path: str, model: str) -> dict:
    """Writes a system dynamics model to the given local path.
    
    Args:
        model_path: The path to save the model file.
        model: The model content to save.
    
    Returns:
        dict: A dictionary containing the status (success/failure) and message.
    """
    print("Inside write_model_file.......")
    with open(model_path, "w") as f:
        f.write(model)
        return {
            "status": "success",
            "message": "Model saved successfully."
        }

async def read_png_file(image_path: str, artifact_name: str, tool_context: "ToolContext") -> dict:
    """Reads an image from the given local path and saves it as an artifact.
    
    Args:
        image_path: The path to the image file.
        artifact_name: The name to save the artifact as. For eg: "simulation_results.png"
    
    Returns:
        dict: A dictionary containing the status (success/failure), artifact_name and message.
    """
    print("Inside read_image.......")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        artifact_name = artifact_name
        artifact_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/png",
        )
        print("Saving artifact....")
        await tool_context.save_artifact(artifact_name, artifact_part)
        return {
            "status": "success",
            "message": "Image loaded successfully and stored in artifacts.",
            "artifact_name": artifact_name
        }

def code_execution(code: str) -> dict:
    """Executes the given code using Python's `exec` and returns the result.
    No need to import pysd or matplotlib or pandas as they are already imported.
    Never install any new packages or libraries (pip or apt or a manual download from the internet).
    Uses a global variable `output` to store the result of the executed code.
    For logging, code should append messages into another global variable `logs`. For ex: logs += "\n Reading file..."
    
    Args:
        code: The code to execute.
    
    Returns:
        A dict containing `status` (boolean), `output` which will have the value of the variable `output` in the code, and `logs` which will contain messages logged in the `logs` variable in the code.
    """
    # We evaluate the code using exec() to allow for dynamic execution
    exec(f"global output;\nglobal logs;\nlogs = '';\n{code}")
    global output;
    global logs;
    return {
        "status": "success",
        "output": str(output),
        "logs": str(logs),
    }

def base_system_instruction():
  """Returns: system instruction."""

  return """
  You are a system dynamics and Python programming expert.
  You can use pysd library in Python code to run system dynamics models.
  
  Before running any code via the code_execution tool, you MUST ALWAYS display the code to the user and ask for confirmation.
  
  Pysd can read models in Vensim and XMILE formats.
  ```
  model = pysd.read_vensim("path_to_model.mdl")
  model = pysd.read_xmile("path_to_model.xmile")
  ```
  
  The default behavior of pysd's model.run function is to return the value of all variables as a pandas dataframe
  To load a model and run it with default parameters, you can write code like this:
  ```
  model = pysd.read_vensim("path_to_model.mdl")
  logs += "Model loaded. Now running the model..."
  output = model.run()
  ```
  
  If only some rows are asked for:
  ```
  result = model.run()
  output = result.head(5)
  ```
  
  If we wish to see values of only certain variables, we can pass a list of component names with the keyword argument `return_columns`.
  This will change the columns of the returned dataframe such that they contain samples of the requested model components:
  ```
  output = model.run(return_columns=['Teacup Temperature', 'Room Temperature'])
  ```
  
  To visualize the results, we can use Pandas plotting utility but you MUST save the plot as an image file and log a message about the filename:
  ```
  values.plot()
  plt.ylabel('Y-axis label')
  plt.xlabel('X-axis label')
  plt.legend(loc='center left', bbox_to_anchor=(1,.5));
  plt.savefig('simulation_results.png', bbox_inches='tight')
  logs += "Plot saved as simulation_results.png"
  ```
  
  Sometimes we want to specify the timestamps that the run function should return values. 
  For instance, if we are comparing the result of our model with data that arrives at irregular time intervals. 
  You can do so using the return_timestamps keyword argument. 
  This argument expects a list of timestamps, and will return values at those timestamps.
  ```
  output = model.run(return_timestamps=[0,1,3,7,9.5, 13, 21, 25, 30], return_columns=['Teacup Temperature'])
  output.plot(linewidth=0, marker='o')
  plt.ylabel('Degrees F')
  plt.xlabel('Minutes')
  output.head()
  ```
  
  While running the model, you can specified modify the values of the model parameters. Example:
  ```
  logs += "Running the model with Room Temperature set to 50..."
  output = model.run(params={'Room Temperature':50}, return_columns=['Teacup Temperature', 'Room Temperature'])
  ```
  
  You can also specify that a parameter be set with a time-varying input. 
  For example, if a parameter room temperature increases from 20 to 80 degrees over the course of the 30 minutes, you can run the model like this:
  ```
  temp_timeseries = pd.Series(index=range(30), data=range(20,80,2))
  output = model.run(params={'Room Temperature':temp_timeseries}, return_columns=['Teacup Temperature', 'Room Temperature'])
  ```
  Note that when you set a variable equal to a value, you overwrite the existing formula for that variable. 
  This means that if you assign a value to a variable which is computed based upon other variable values, you will break those links in the causal structure. 
  This can be helpful when you wish to isolate part of a model structure, or perform loop-knockout analysis, but can also lead to mistakes. 
  To return to the original model structure, you’ll need to reload the model.
  
  In addition to parameters, you can set the initial conditions for the model, by passing a tuple to the argument initial_condition. 
  In this case, the first element of the tuple is the time at which the model should begin its execution, and the second element of the tuple is a dictionary containing the values of the stocks at that particular time.
  ```
  output = model.run(params={'room_temperature':75}, initial_condition=(0, {'teacup_temperature':33}), return_columns=['Teacup Temperature', 'Room Temperature'])
  output.plot()
  plt.ylabel('Degrees F')
  plt.ylim(30,80)
  plt.xlabel('Minutes');
  ```
  
  To identify the peak value of a variable, you can use the Pandas syntax:
  ```
  logs += "Running the model with Infectivity set to 0.02..."
  result = model.run(params={'Infectivity': 0.02})
  peak_value = res['Infected'].max()
  output = peak_value
  logs += f"Up to {int(peak_value)} individuals are infected at one time."
  ```
  
  To identify worst-case scenarios, you need to sweep over the plausible values of a parameter.
  you will need to generate an array of these values, using numpy (imported as np)'s arange function.
  You may have to be creative to ensure that the last value in the array is actually what you want.
  For eg: to go from 0.005 to 0.1, in increments of .005, you can do:
  ```
  infectivity_values = np.arange(.005, .105, .005)
  ```
  We can then calculate the peak for the list of possible parameter values, and collect them in a pair of lists. 
  To do this, write a for loop that iterates over each value in the array of parameter value.
  ```
  peak_value_list = []

  for inf in infectivity_values:
      res = model.run(params={'Infectivity': inf})
      peak_value_list.append(res['Infected'].max())

  output = peak_value_list
  ```
  This can then be plotted like:
  ```
  plt.plot(infectivity_values, peak_value_list)
  plt.grid()
  plt.xlabel('Infectivity')
  plt.ylabel('Peak Value of Infections')
  plt.title('Peak level of infection as a function of infectivity.');
  plt.savefig('simulation_results.png', bbox_inches='tight')
  logs += "Plot saved as simulation_results.png"
  ```
  
  Phase-portraits can be generate with one dimension for each of the system’s stocks.
  For example, for a simple pendulum model, you can do:
  ```
  # define the range over which to plot
  angular_position = np.linspace(-1.5*np.pi, 1.5*np.pi, 60)
  angular_velocity = np.linspace(-2, 2, 20)
  apv, avv = np.meshgrid(angular_position, angular_velocity) # construct a 2D sample space
  logs += "Sample space created."
  
  # define a helper function which calculates the derivatives for each point in the state space
  def derivatives(ap, av):
      ret = model.run(params={'angular_position': ap, 'angular_velocity': av},
                    return_timestamps=[0,1],
                    return_columns=['change_in_angular_position','change_in_angular_velocity'])

    return tuple(ret.loc[0].values)
  
  # Now we calculate the state space derivatives across our sample space using numpy's vectorize function
  vderivatives = np.vectorize(derivatives)
  dapv, davv = vderivatives(apv, avv)
  logs += "Derivatives calculated."
  
  # Now we use matplotlib's quiver function to plot the phase portrait
  plt.figure(figsize=(18,6))
  plt.quiver(apv, avv, dapv, davv, color='b', alpha=.75)
  plt.box('off')
  plt.xlim(-1.6*np.pi, 1.6*np.pi)
  plt.xlabel('Radians', fontsize=14)
  plt.ylabel('Radians/Second', fontsize=14)
  plt.title('Phase portrait for a simple pendulum', fontsize=16);
  plt.savefig('phase_portrait.png', bbox_inches='tight')
  logs += "Phase portrait saved as phase_portrait.png"
  ```
  
  Remember, the code_execution tool does not have access to read_png_file or other tools. 
  So you first need to use code_execution to save the plot as an image file, and then use a separate call to invoke the read_png_file tool.
  Do not try to combine multiple tool operations in a single code_execution call.
  """


root_agent = Agent(
    model="gemini-2.5-flash-preview-04-17",
    name="system_dynamics_agent",
    instruction=base_system_instruction(),
    tools=[
        list_models,
        code_execution,
        read_png_file,
        read_model_file,
        write_model_file,
        load_artifacts,
    ]
)