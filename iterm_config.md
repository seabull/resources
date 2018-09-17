### Config iTerm2 

#### Prerequisites

- Install Homebrew, iTerm2 and zsh (or oh-my-zsh)

- Choose and set a color scheme 

  - `iTerm -> Preferences -> Profiles -> Colors -> Color Presets -> Import` then select the colour scheme you like, such as the Dracula and Solarised Dark themes
  - [Dracula Theme](https://draculatheme.com/iterm/) for iTerm2

- Download Nerd Fonts and configure iTerm2 to use it

  - [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts#font-installation)

  - Download and install using curl.

    ```
    cd ~/Library/Fonts && curl -fLo "Droid Sans Mono for Powerline Nerd Font Complete.otf" https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/DroidSansMono/complete/Droid%20Sans%20Mono%20Nerd%20Font%20Complete.otf
    ```

  - Configure iTerm2 with Nerd Fonts

    ```
    iTerm2 -> Preferences -> Profiles -> Text -> Font -> Change Font
    ```

    Select the font **Droid Sans Mono Nerd Font Complete** and adjust the size if your want too. Also check the box for `Use a different font for non-ASCII text` and select the font again. It should be displaying the new font and icons in the prompt.

- Add [Powerlevel9K](https://github.com/bhilburn/powerlevel9k/wiki/Install-Instructions#step-1-install-powerlevel9k) theme for Zsh

  - Installation

    - You need to tell Powerlevel9k to use the Nerd Fonts in your `~/.zshrc`.

      ```
      echo "POWERLEVEL9K_MODE='nerdfont-complete'" >> ~/.zshrc
      ```

      Next install the Powerleve9k theme from [GitHub](https://github.com/bhilburn/powerlevel9k) and add the command to load it when Zsh starts.

      ```
      git clone https://github.com/bhilburn/powerlevel9k.git ~/powerlevel9k
      echo 'source  ~/powerlevel9k/powerlevel9k.zsh-theme' >> ~/.zshrc
      ```

      **Note**: The font needs to be set before Powerlevel9k is initialised in order to use it. If you open your `~/.zshrc`, it should have the commands in this order.

      ```
      POWERLEVEL9K_MODE='nerdfont-complete'
      source ~/powerlevel9k/powerlevel9k.zsh-theme
      ```

  - Customize your prompt

    - To change your setup, open your `~/.zshrc` and add in the [configuration](https://github.com/bhilburn/powerlevel9k#prompt-customization) you prefer. It’s best practice to declare all the configuration before you call the Powerlevel9k theme’s script. This is an example of a basic setup, which is listed in my `~/.zshrc`.

      ```
      POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(dir vcs newline status)
      POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=()
      POWERLEVEL9K_PROMPT_ADD_NEWLINE=true
      POWERLEVEL9K_MODE='nerdfont-complete'
      source ~/powerlevel9k/powerlevel9k.zsh-theme
      ```

      Powerlevel9k allows you to easily add custom prompt segments by adding them to certain environment variables. It has to follow the below syntax, where they are prefixed by “custom”. This is the configuration for the custom Medium and freeCodeCamp elements used in the terminal screenshots at the top of this article.

      ```
      # Customise the Powerlevel9k prompts
      POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(
        custom_medium custom_freecodecamp dir vcs newline status
      )
      POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=()
      POWERLEVEL9K_PROMPT_ADD_NEWLINE=true
      # Add the custom Medium M icon prompt segment
      POWERLEVEL9K_CUSTOM_MEDIUM="echo -n '\uF859'"
      POWERLEVEL9K_CUSTOM_MEDIUM_FOREGROUND="black"
      POWERLEVEL9K_CUSTOM_MEDIUM_BACKGROUND="white"
      # Add the custom freeCodeCamp prompt segment
      POWERLEVEL9K_CUSTOM_FREECODECAMP="echo -n ’\uE242' freeCodeCamp"
      POWERLEVEL9K_CUSTOM_FREECODECAMP_FOREGROUND="white"
      POWERLEVEL9K_CUSTOM_FREECODECAMP_BACKGROUND="cyan"
      ```

      #### Set variable names for a custom prompt section

      Powerlevel9k includes code to dynamically create prompt elements based on environment variables. Follow this structure to add your own custom prompt section.

      → Add `custom_<YOUR PROMPT SECTION NAME>` to `POWERLEVEL9K_LEFT_PROMPT_ELEMENTS` or `POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS`

      → Set a color for `POWERLEVEL9K_CUSTOM_<YOUR PROMPT SECTION NAME>_FOREGROUND`

      → Set a color for `POWERLEVEL9K_CUSTOM_<YOUR PROMPT SECTION NAME>_BACKGROUND`

      → Set the icon and text for the content of the section defined to `POWERLEVEL9K_CUSTOM_<YOUR PROMPT SECTION NAME>`

  - 

