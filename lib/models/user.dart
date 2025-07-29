class User {
  final String id;
  final String email;
  final String username;
  final String? displayName;
  final String? avatarUrl;
  final DateTime createdAt;
  final DateTime? lastLoginAt;
  final Map<String, dynamic> preferences;
  final int totalPredictions;
  final int correctPredictions;
  final double accuracy;

  User({
    required this.id,
    required this.email,
    required this.username,
    this.displayName,
    this.avatarUrl,
    required this.createdAt,
    this.lastLoginAt,
    this.preferences = const {},
    this.totalPredictions = 0,
    this.correctPredictions = 0,
    this.accuracy = 0.0,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      username: json['username'] ?? '',
      displayName: json['display_name'],
      avatarUrl: json['avatar_url'],
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
      lastLoginAt: json['last_login_at'] != null 
          ? DateTime.tryParse(json['last_login_at']) 
          : null,
      preferences: json['preferences'] ?? {},
      totalPredictions: json['total_predictions'] ?? 0,
      correctPredictions: json['correct_predictions'] ?? 0,
      accuracy: (json['accuracy'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'username': username,
      'display_name': displayName,
      'avatar_url': avatarUrl,
      'created_at': createdAt.toIso8601String(),
      'last_login_at': lastLoginAt?.toIso8601String(),
      'preferences': preferences,
      'total_predictions': totalPredictions,
      'correct_predictions': correctPredictions,
      'accuracy': accuracy,
    };
  }

  @override
  String toString() {
    return 'User(id: $id, username: $username, email: $email)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 