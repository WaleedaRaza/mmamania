class UserStats {
  final String userId;
  final int eloRating;
  final int totalPredictions;
  final int correctPredictions;
  final double accuracy;
  final int currentStreak;
  final int bestStreak;
  final int totalPoints;
  final DateTime lastPredictionDate;
  final Map<String, int> divisionStats; // Predictions per weight class

  UserStats({
    required this.userId,
    this.eloRating = 1500,
    this.totalPredictions = 0,
    this.correctPredictions = 0,
    this.accuracy = 0.0,
    this.currentStreak = 0,
    this.bestStreak = 0,
    this.totalPoints = 0,
    required this.lastPredictionDate,
    this.divisionStats = const {},
  });

  factory UserStats.fromJson(Map<String, dynamic> json) {
    return UserStats(
      userId: json['user_id'] ?? '',
      eloRating: json['elo_rating'] ?? 1500,
      totalPredictions: json['total_predictions'] ?? 0,
      correctPredictions: json['correct_predictions'] ?? 0,
      accuracy: (json['accuracy'] ?? 0.0).toDouble(),
      currentStreak: json['current_streak'] ?? 0,
      bestStreak: json['best_streak'] ?? 0,
      totalPoints: json['total_points'] ?? 0,
      lastPredictionDate: json['last_prediction_date'] != null 
          ? DateTime.parse(json['last_prediction_date']) 
          : DateTime.now(),
      divisionStats: Map<String, int>.from(json['division_stats'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'elo_rating': eloRating,
      'total_predictions': totalPredictions,
      'correct_predictions': correctPredictions,
      'accuracy': accuracy,
      'current_streak': currentStreak,
      'best_streak': bestStreak,
      'total_points': totalPoints,
      'last_prediction_date': lastPredictionDate.toIso8601String(),
      'division_stats': divisionStats,
    };
  }

  UserStats copyWith({
    String? userId,
    int? eloRating,
    int? totalPredictions,
    int? correctPredictions,
    double? accuracy,
    int? currentStreak,
    int? bestStreak,
    int? totalPoints,
    DateTime? lastPredictionDate,
    Map<String, int>? divisionStats,
  }) {
    return UserStats(
      userId: userId ?? this.userId,
      eloRating: eloRating ?? this.eloRating,
      totalPredictions: totalPredictions ?? this.totalPredictions,
      correctPredictions: correctPredictions ?? this.correctPredictions,
      accuracy: accuracy ?? this.accuracy,
      currentStreak: currentStreak ?? this.currentStreak,
      bestStreak: bestStreak ?? this.bestStreak,
      totalPoints: totalPoints ?? this.totalPoints,
      lastPredictionDate: lastPredictionDate ?? this.lastPredictionDate,
      divisionStats: divisionStats ?? this.divisionStats,
    );
  }

  // Calculate new ELO after a prediction result
  UserStats updateAfterPrediction(bool isCorrect, int opponentElo) {
    final kFactor = 32; // Standard K-factor for ELO
    final expectedScore = 1 / (1 + pow(10, (opponentElo - eloRating) / 400));
    final actualScore = isCorrect ? 1.0 : 0.0;
    final newElo = eloRating + (kFactor * (actualScore - expectedScore)).round();
    
    final newTotalPredictions = totalPredictions + 1;
    final newCorrectPredictions = correctPredictions + (isCorrect ? 1 : 0);
    final newAccuracy = newCorrectPredictions / newTotalPredictions;
    
    final newCurrentStreak = isCorrect ? currentStreak + 1 : 0;
    final newBestStreak = newCurrentStreak > bestStreak ? newCurrentStreak : bestStreak;
    
    final eloChange = newElo - eloRating;
    final newTotalPoints = totalPoints + (isCorrect ? 10 + eloChange : eloChange);
    
    return copyWith(
      eloRating: newElo,
      totalPredictions: newTotalPredictions,
      correctPredictions: newCorrectPredictions,
      accuracy: newAccuracy,
      currentStreak: newCurrentStreak,
      bestStreak: newBestStreak,
      totalPoints: newTotalPoints,
      lastPredictionDate: DateTime.now(),
    );
  }

  // Get rank based on ELO
  String getRank() {
    if (eloRating >= 2000) return 'Grandmaster';
    if (eloRating >= 1800) return 'Master';
    if (eloRating >= 1600) return 'Expert';
    if (eloRating >= 1400) return 'Advanced';
    if (eloRating >= 1200) return 'Intermediate';
    return 'Beginner';
  }

  // Get rank color
  int getRankColor() {
    if (eloRating >= 2000) return 0xFFFFD700; // Gold
    if (eloRating >= 1800) return 0xFFC0C0C0; // Silver
    if (eloRating >= 1600) return 0xFFCD7F32; // Bronze
    if (eloRating >= 1400) return 0xFF4CAF50; // Green
    if (eloRating >= 1200) return 0xFF2196F3; // Blue
    return 0xFF9E9E9E; // Grey
  }
}

double pow(double x, double exponent) {
  return x * (exponent > 0 ? 1 : -1);
} 