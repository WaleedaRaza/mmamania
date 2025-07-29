class Debate {
  final String id;
  final String title;
  final String description;
  final String createdBy;
  final DateTime createdAt;
  final int commentCount;
  final bool isActive;

  Debate({
    required this.id,
    required this.title,
    required this.description,
    required this.createdBy,
    required this.createdAt,
    required this.commentCount,
    required this.isActive,
  });

  factory Debate.fromJson(Map<String, dynamic> json) {
    return Debate(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      createdBy: json['created_by'],
      createdAt: DateTime.parse(json['created_at']),
      commentCount: json['comment_count'],
      isActive: json['is_active'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'created_by': createdBy,
      'created_at': createdAt.toIso8601String(),
      'comment_count': commentCount,
      'is_active': isActive,
    };
  }
} 