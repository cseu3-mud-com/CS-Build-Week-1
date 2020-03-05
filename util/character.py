character = {
    'direction': {
      'types': ['back', 'front', 'left', 'right']
    },
    'sex': {
      "types": ['male', 'female'],
    },
    'body': {
      'types': ['human'], #'reptiles', 'orcs', 'skeleton', 'special', 'pregnant', 'child'
      "colors": [
        ['white', 'black', 'olive', 'brown', 'peach', 'light', 'dark', 'dark2', 'tanned', 'tanned2'] #  'muscular_white', 'muscular_dark'
      ],
      "sprites": 'body/{sex}/{color}.png'
    },
    'hair': {
      "types": ['plain', 'bedhead', 'loose'],
      "types_sex": [ # supposed to restrict hair style to specific gender
        'male', 'male', 'female'
      ],
      "colors": [
        # plain
        ['blonde', 'blue', 'brunette', 'green', 'pink', 'raven', 'dark_blonde', 'white_blonde'],
        # bedhead
        ['blonde', 'blue', 'brunette', 'green', 'pink', 'raven', 'redhead', 'white_blonde'],
        # loose
        ['black', 'blonde', 'blonde2', 'blue', 'blue2', 'brown', 'brunette', 'brunette2', 'dark-blonde', 'gray', 'green', 'green2', 'light-blonde', 'light-blonde2', 'pink', 'pink2', 'raven', 'raven2', 'redhead', 'ruby-red', 'white', 'white-blonde', 'white-blonde2', 'white-cyan'],
      ],
      "sprites": 'hair/{sex}/{type}/{color}.png'
    },
    'hats': {
      "types": [],
      "sprites": []
    },
    'eyes': {
      'types': [],
      'sprites': []
    },
    'facial': {
      'types': [],
      'sprites': []
    },
    'nose': {
      'types': [],
      'sprites': []
    },
    'ears': {
      'types': [],
      'sprites': []
    },
    'jacket': {
      'types': [],
      'sprites': []
    },
    'clothes': {
      'types': [],
      'sprites': []
    },
    'legs': {
      'types': [],
      'sprites': []
    },
    'shoes': {
      'types': [],
      'sprites': []
    },
    'boots': {
      'types': [],
      'sprites': []
    },
    'weapon': {
      'types': [],
      'sprites': []
    },
    'ammo': {
      'types': [],
      'sprites': []
    }
}