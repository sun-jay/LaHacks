# Winner at LA Hacks 2024 under the Fetch.ai Sponsor track - [Devpost](https://devpost.com/software/agent-acumen)
## Inspiration
The inspiration for Agent Acumen struck during a conversation with my aunt, an orthodontist, who shared her frustrations about how much of her workday is consumed by repetitive, low-level tasks. These tasks divert her attention from patient care, which is her primary role and passion. Realizing that language models like ChatGPT can manage intellectual tasks, it sparked the idea to extend this capability into physical tasks through a robotic system. This would allow healthcare professionals to focus more on patient interactions rather than mundane tasks.

## What it does
Agent Acumen is designed to revolutionize the healthcare workspace by automating routine physical tasks through a highly intelligent robotic system. Utilizing advanced computer vision and machine learning, it precisely identifies, picks, and moves medical tools and supplies from one location to another as instructed. This automation includes tasks like moving tools from a disinfectant bath to a discard bin, effectively reducing the workload and minimizing the time spent on non-clinical tasks by healthcare staff.

## How we built it
Building Agent Acumen within a tight 36-hour timeframe required rapid innovation and efficient problem-solving. Here’s how we brought it to life:

- **Advanced Robotics**: Developed a fully 3D printed, open-source robotic arm, specifically tailored for the healthcare environment, ensuring compliance with industry standards and adaptability for various medical tasks.

- **Vision System**: Leveraging Google’s Gemini pro and Fetch.AI, the system captures images and overlays object centroids using OpenCV, facilitating precise interaction with objects found in healthcare settings.

- **Semantic Execution**: Utilizes Gemini’s advanced semantic understanding to interpret user commands and facilitate decision-making for dynamic object manipulation.

- **Custom Kinematics**: We developed custom kinematics and inverse kinematics to ensure the robotic arm movements are accurate and can reach all necessary points within its operational environment.

- **Firmware and Control**: Custom PWM motor firmware, written in C++, manages the precise control needed for detailed healthcare operations.

- **Real-Time Audio Transcription**: Utilizing Distil-Whisper, accelerated on Apple’s M2 GPU with PyTorch and Metal framework, the system offers always-on, on-device real-time audio transcription for hands-free operation. Give the same in markup language

Through these technologies, Agent Acumen brings the concept of low-level task automation from digital to physical, mirroring the efficiency seen in intelligent language models but in a tangible, impactful manner in healthcare settings.

## Challenges we ran into
Building Agent Acumen was an ambitious project that involved complex integrations and ideas. Here are some of the key challenges we encountered:

- **3D Printing the Robotic Arm**: 
  - Designing and printing a fully functional robotic arm from scratch.
  - Ensuring the durability and precision of 3D-printed components under operational stress.

- **Assembling and Wiring**:
  - Integrating sophisticated electronics, including motors, controllers, and sensors.
  - Managing complex wiring and circuit setups to ensure reliable connectivity and performance.

- **Understanding and Implementing Fetch.AI**:
  - Grasping the advanced concepts and frameworks provided by Fetch.AI.
  - Customizing and deploying these AI solutions effectively within our system to handle real-time decisions.

- **Prompt Engineering**:
  - Developing precise and contextually relevant prompts for Gemini to interpret and act upon.
  - Ensuring that the AI understands and executes tasks based on dynamic user inputs in a healthcare environment.

- **Software Integration**:
  - Integrating various software components to work seamlessly together, including vision processing, motion control, and user interface systems.
  - Overcoming compatibility issues between various modules.

These challenges pushed our team to problem-solve at every turn.
