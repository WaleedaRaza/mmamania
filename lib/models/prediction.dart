import 'package:flutter/foundation.dart';

enum PredictionResult {
  pending,
  correct,
  incorrect,
}

class Prediction {
  final String id;
  final String userId;
  final String fightId;
  final String predictedWinnerId;
  final String? predictedMethod;
  final int? predictedRound;
  final DateTime createdAt;
  final PredictionResult result;
  final int? eloChange;
  final String? actualWinnerId;
  final String? actualMethod;
  final int? actualRound;

  Prediction({
    required this.id,
    required this.userId,
    required this.fightId,
    required this.predictedWinnerId,
    this.predictedMethod,
    this.predictedRound,
    required this.createdAt,
    this.result = PredictionResult.pending,
    this.eloChange,
    this.actualWinnerId,
    this.actualMethod,
    this.actualRound,
  });

  factory Prediction.fromJson(Map<String, dynamic> json) {
    return Prediction(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      fightId: json['fight_id'] ?? '',
      predictedWinnerId: json['predicted_winner_id'] ?? '',
      predictedMethod: json['predicted_method'],
      predictedRound: json['predicted_round'],
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : DateTime.now(),
      result: PredictionResult.values.firstWhere(
        (e) => e.toString().split('.').last == json['result'],
        orElse: () => PredictionResult.pending,
      ),
      eloChange: json['elo_change'],
      actualWinnerId: json['actual_winner_id'],
      actualMethod: json['actual_method'],
      actualRound: json['actual_round'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'fight_id': fightId,
      'predicted_winner_id': predictedWinnerId,
      'predicted_method': predictedMethod,
      'predicted_round': predictedRound,
      'created_at': createdAt.toIso8601String(),
      'result': result.toString().split('.').last,
      'elo_change': eloChange,
      'actual_winner_id': actualWinnerId,
      'actual_method': actualMethod,
      'actual_round': actualRound,
    };
  }

  Prediction copyWith({
    String? id,
    String? userId,
    String? fightId,
    String? predictedWinnerId,
    String? predictedMethod,
    int? predictedRound,
    DateTime? createdAt,
    PredictionResult? result,
    int? eloChange,
    String? actualWinnerId,
    String? actualMethod,
    int? actualRound,
  }) {
    return Prediction(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      fightId: fightId ?? this.fightId,
      predictedWinnerId: predictedWinnerId ?? this.predictedWinnerId,
      predictedMethod: predictedMethod ?? this.predictedMethod,
      predictedRound: predictedRound ?? this.predictedRound,
      createdAt: createdAt ?? this.createdAt,
      result: result ?? this.result,
      eloChange: eloChange ?? this.eloChange,
      actualWinnerId: actualWinnerId ?? this.actualWinnerId,
      actualMethod: actualMethod ?? this.actualMethod,
      actualRound: actualRound ?? this.actualRound,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Prediction && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 