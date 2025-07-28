class DebateMessage {
  final String id;
  final String debateId;
  final String userId;
  final String username;
  final String message;
  final DateTime createdAt;
  final int likes;
  final bool isEdited;

  DebateMessage({
    required this.id,
    required this.debateId,
    required this.userId,
    required this.username,
    required this.message,
    required this.createdAt,
    required this.likes,
    required this.isEdited,
  });

  factory DebateMessage.fromJson(Map<String, dynamic> json) {
    return DebateMessage(
      id: json['id'],
      debateId: json['debate_id'],
      userId: json['user_id'],
      username: json['username'],
      message: json['message'],
      createdAt: DateTime.parse(json['created_at']),
      likes: json['likes'] ?? 0,
      isEdited: json['is_edited'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'debate_id': debateId,
      'user_id': userId,
      'username': username,
      'message': message,
      'created_at': createdAt.toIso8601String(),
      'likes': likes,
      'is_edited': isEdited,
    };
  }
} 