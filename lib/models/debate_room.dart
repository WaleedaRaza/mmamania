enum DebateRoomStatus {
  waiting,
  active,
  paused,
  ended,
  full,
}

enum DebateRoomType {
  text,
  audio,
  video,
}

class DebateRoom {
  final String id;
  final String title;
  final String description;
  final String createdBy;
  final DateTime createdAt;
  final int participantCount;
  final int maxParticipants;
  final bool isActive;
  final DebateRoomStatus status;
  final DebateRoomType type;
  final String? topic;
  final String? category;
  final List<String> tags;
  final Map<String, dynamic>? audioSettings;
  final DateTime? startedAt;
  final DateTime? endedAt;
  final int currentSpeakerIndex;
  final List<String> participantIds;
  final Map<String, dynamic>? metadata;

  DebateRoom({
    required this.id,
    required this.title,
    required this.description,
    required this.createdBy,
    required this.createdAt,
    this.participantCount = 0,
    this.maxParticipants = 10,
    this.isActive = true,
    this.status = DebateRoomStatus.waiting,
    this.type = DebateRoomType.text,
    this.topic,
    this.category,
    this.tags = const [],
    this.audioSettings,
    this.startedAt,
    this.endedAt,
    this.currentSpeakerIndex = 0,
    this.participantIds = const [],
    this.metadata,
  });

  factory DebateRoom.fromJson(Map<String, dynamic> json) {
    return DebateRoom(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      createdBy: json['created_by'],
      createdAt: DateTime.parse(json['created_at']),
      participantCount: json['participant_count'] ?? 0,
      maxParticipants: json['max_participants'] ?? 10,
      isActive: json['is_active'] ?? true,
      status: DebateRoomStatus.values.firstWhere(
        (e) => e.toString() == 'DebateRoomStatus.${json['status']}',
        orElse: () => DebateRoomStatus.waiting,
      ),
      type: DebateRoomType.values.firstWhere(
        (e) => e.toString() == 'DebateRoomType.${json['type']}',
        orElse: () => DebateRoomType.text,
      ),
      topic: json['topic'],
      category: json['category'],
      tags: (json['tags'] as List<dynamic>?)?.cast<String>() ?? [],
      audioSettings: json['audio_settings'],
      startedAt: json['started_at'] != null ? DateTime.parse(json['started_at']) : null,
      endedAt: json['ended_at'] != null ? DateTime.parse(json['ended_at']) : null,
      currentSpeakerIndex: json['current_speaker_index'] ?? 0,
      participantIds: (json['participant_ids'] as List<dynamic>?)?.cast<String>() ?? [],
      metadata: json['metadata'],
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
      'max_participants': maxParticipants,
      'is_active': isActive,
      'status': status.toString().split('.').last,
      'type': type.toString().split('.').last,
      'topic': topic,
      'category': category,
      'tags': tags,
      'audio_settings': audioSettings,
      'started_at': startedAt?.toIso8601String(),
      'ended_at': endedAt?.toIso8601String(),
      'current_speaker_index': currentSpeakerIndex,
      'participant_ids': participantIds,
      'metadata': metadata,
    };
  }

  DebateRoom copyWith({
    String? id,
    String? title,
    String? description,
    String? createdBy,
    DateTime? createdAt,
    int? participantCount,
    int? maxParticipants,
    bool? isActive,
    DebateRoomStatus? status,
    DebateRoomType? type,
    String? topic,
    String? category,
    List<String>? tags,
    Map<String, dynamic>? audioSettings,
    DateTime? startedAt,
    DateTime? endedAt,
    int? currentSpeakerIndex,
    List<String>? participantIds,
    Map<String, dynamic>? metadata,
  }) {
    return DebateRoom(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      createdBy: createdBy ?? this.createdBy,
      createdAt: createdAt ?? this.createdAt,
      participantCount: participantCount ?? this.participantCount,
      maxParticipants: maxParticipants ?? this.maxParticipants,
      isActive: isActive ?? this.isActive,
      status: status ?? this.status,
      type: type ?? this.type,
      topic: topic ?? this.topic,
      category: category ?? this.category,
      tags: tags ?? this.tags,
      audioSettings: audioSettings ?? this.audioSettings,
      startedAt: startedAt ?? this.startedAt,
      endedAt: endedAt ?? this.endedAt,
      currentSpeakerIndex: currentSpeakerIndex ?? this.currentSpeakerIndex,
      participantIds: participantIds ?? this.participantIds,
      metadata: metadata ?? this.metadata,
    );
  }

  bool get isAudioRoom => type == DebateRoomType.audio || type == DebateRoomType.video;
  bool get isFull => participantCount >= maxParticipants;
  bool get canJoin => isActive && !isFull && status != DebateRoomStatus.ended;
  Duration? get duration => startedAt != null ? DateTime.now().difference(startedAt!) : null;
} 