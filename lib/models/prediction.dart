class Prediction {
  final String id;
  final String fightId;
  final String userId;
  final String winner;
  final String method;
  final int round;
  final double confidence;
  final DateTime createdAt;

  Prediction({
    required this.id,
    required this.fightId,
    required this.userId,
    required this.winner,
    required this.method,
    required this.round,
    required this.confidence,
    required this.createdAt,
  });

  factory Prediction.fromJson(Map<String, dynamic> json) {
    return Prediction(
      id: json['id'],
      fightId: json['fight_id'],
      userId: json['user_id'],
      winner: json['winner'],
      method: json['method'],
      round: json['round'],
      confidence: json['confidence'].toDouble(),
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'fight_id': fightId,
      'user_id': userId,
      'winner': winner,
      'method': method,
      'round': round,
      'confidence': confidence,
      'created_at': createdAt.toIso8601String(),
    };
  }
} 