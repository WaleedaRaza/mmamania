class DebateRoom {
  final String id;
  final String title;
  final String description;
  final String createdBy;
  final DateTime createdAt;
  final int participantCount;
  final bool isActive;
  final String status;

  DebateRoom({
    required this.id,
    required this.title,
    required this.description,
    required this.createdBy,
    required this.createdAt,
    required this.participantCount,
    required this.isActive,
    required this.status,
  });

  factory DebateRoom.fromJson(Map<String, dynamic> json) {
    return DebateRoom(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      createdBy: json['created_by'],
      createdAt: DateTime.parse(json['created_at']),
      participantCount: json['participant_count'] ?? 0,
      isActive: json['is_active'] ?? true,
      status: json['status'] ?? 'Active',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'created_by': createdBy,
      'created_at': createdAt.toIso8601String(),
      'participant_count': participantCount,
      'is_active': isActive,
      'status': status,
    };
  }
} 