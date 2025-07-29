enum MessageType {
  text,
  system,
  audio,
  reaction,
  command,
}

enum MessageStatus {
  sending,
  sent,
  delivered,
  read,
  failed,
}

class RealtimeMessage {
  final String id;
  final String roomId;
  final String userId;
  final String username;
  final String? avatarUrl;
  final String content;
  final MessageType type;
  final MessageStatus status;
  final DateTime timestamp;
  final DateTime? editedAt;
  final List<String> reactions;
  final Map<String, dynamic>? metadata;
  final bool isEdited;
  final bool isDeleted;

  RealtimeMessage({
    required this.id,
    required this.roomId,
    required this.userId,
    required this.username,
    this.avatarUrl,
    required this.content,
    this.type = MessageType.text,
    this.status = MessageStatus.sent,
    required this.timestamp,
    this.editedAt,
    this.reactions = const [],
    this.metadata,
    this.isEdited = false,
    this.isDeleted = false,
  });

  factory RealtimeMessage.fromJson(Map<String, dynamic> json) {
    return RealtimeMessage(
      id: json['id'],
      roomId: json['room_id'],
      userId: json['user_id'],
      username: json['username'],
      avatarUrl: json['avatar_url'],
      content: json['content'],
      type: MessageType.values.firstWhere(
        (e) => e.toString() == 'MessageType.${json['type']}',
        orElse: () => MessageType.text,
      ),
      status: MessageStatus.values.firstWhere(
        (e) => e.toString() == 'MessageStatus.${json['status']}',
        orElse: () => MessageStatus.sent,
      ),
      timestamp: DateTime.parse(json['timestamp']),
      editedAt: json['edited_at'] != null ? DateTime.parse(json['edited_at']) : null,
      reactions: (json['reactions'] as List<dynamic>?)?.cast<String>() ?? [],
      metadata: json['metadata'],
      isEdited: json['is_edited'] ?? false,
      isDeleted: json['is_deleted'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'room_id': roomId,
      'user_id': userId,
      'username': username,
      'avatar_url': avatarUrl,
      'content': content,
      'type': type.toString().split('.').last,
      'status': status.toString().split('.').last,
      'timestamp': timestamp.toIso8601String(),
      'edited_at': editedAt?.toIso8601String(),
      'reactions': reactions,
      'metadata': metadata,
      'is_edited': isEdited,
      'is_deleted': isDeleted,
    };
  }

  RealtimeMessage copyWith({
    String? id,
    String? roomId,
    String? userId,
    String? username,
    String? avatarUrl,
    String? content,
    MessageType? type,
    MessageStatus? status,
    DateTime? timestamp,
    DateTime? editedAt,
    List<String>? reactions,
    Map<String, dynamic>? metadata,
    bool? isEdited,
    bool? isDeleted,
  }) {
    return RealtimeMessage(
      id: id ?? this.id,
      roomId: roomId ?? this.roomId,
      userId: userId ?? this.userId,
      username: username ?? this.username,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      content: content ?? this.content,
      type: type ?? this.type,
      status: status ?? this.status,
      timestamp: timestamp ?? this.timestamp,
      editedAt: editedAt ?? this.editedAt,
      reactions: reactions ?? this.reactions,
      metadata: metadata ?? this.metadata,
      isEdited: isEdited ?? this.isEdited,
      isDeleted: isDeleted ?? this.isDeleted,
    );
  }

  bool get isSystemMessage => type == MessageType.system;
  bool get isAudioMessage => type == MessageType.audio;
  bool get isReaction => type == MessageType.reaction;
  bool get isCommand => type == MessageType.command;
  
  Duration get age => DateTime.now().difference(timestamp);
  bool get isRecent => age.inMinutes < 5;
} 