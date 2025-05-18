from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"yes": "dis a response"})

@app.route('/api/interest_groups/info')
def interest_groups_info():
    return jsonify([
    {
      name: "Chess",
      description:
        "Play a fun game that keeps your brain sharp. Learn new moves!",
    },
    {
      name: "Checkers",
      description:
        "A classic game! Easy to learn, fun to play. Use your thinking.",
    },
    {
      name: "Mahjong",
      description:
        "Play with tiles! A classic game from far away. Good for your mind and friends.",
    },
    {
      name: "Poker",
      description:
        "Play cards together! A fun game. Use your quick thinking. Just for fun!",
    },
    {
      name: "Yoga",
      description: "Gentle moves to feel good. Helps you bend and feel calm.",
    },
    {
      name: "Photography",
      description:
        "Take pictures! Use your camera or phone. Show what you see.",
    },
  ])
