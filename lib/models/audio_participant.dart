enum ParticipantRole {
  host,
  coHost,
  speaker,
  listener,
  moderator,
}

enum ParticipantStatus {
  connected,
  disconnected,
  speaking,
  muted,
  raisedHand,
  away,
}

class AudioParticipant {
  final String id;
  final String userId;
  final String username;
  final String? avatarUrl;
  final String roomId;
  final ParticipantRole role;
  final ParticipantStatus status;
  final bool isMuted;
  final bool isSpeaking;
  final bool hasRaisedHand;
  final DateTime joinedAt;
  final DateTime? lastSpokeAt;
  final int totalSpeakTime;
  final Map<String, dynamic>? audioStats;
  final List<String> permissions;
  final Map<String, dynamic>? metadata;

  AudioParticipant({
    required this.id,
    required this.userId,
    required this.username,
    this.avatarUrl,
    required this.roomId,
    this.role = ParticipantRole.listener,
    this.status = ParticipantStatus.connected,
    this.isMuted = false,
    this.isSpeaking = false,
    this.hasRaisedHand = false,
    required this.joinedAt,
    this.lastSpokeAt,
    this.totalSpeakTime = 0,
    this.audioStats,
    this.permissions = const [],
    this.metadata,
  });

  factory AudioParticipant.fromJson(Map<String, dynamic> json) {
    return AudioParticipant(
      id: json['id'],
      userId: json['user_id'],
      username: json['username'],
      avatarUrl: json['avatar_url'],
      roomId: json['room_id'],
      role: ParticipantRole.values.firstWhere(
        (e) => e.toString() == 'ParticipantRole.${json['role']}',
        orElse: () => ParticipantRole.listener,
      ),
      status: ParticipantStatus.values.firstWhere(
        (e) => e.toString() == 'ParticipantStatus.${json['status']}',
        orElse: () => ParticipantStatus.connected,
      ),
      isMuted: json['is_muted'] ?? false,
      isSpeaking: json['is_speaking'] ?? false,
      hasRaisedHand: json['has_raised_hand'] ?? false,
      joinedAt: DateTime.parse(json['joined_at']),
      lastSpokeAt: json['last_spoke_at'] != null ? DateTime.parse(json['last_spoke_at']) : null,
      totalSpeakTime: json['total_speak_time'] ?? 0,
      audioStats: json['audio_stats'],
      permissions: (json['permissions'] as List<dynamic>?)?.cast<String>() ?? [],
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'username': username,
      'avatar_url': avatarUrl,
      'room_id': roomId,
      'role': role.toString().split('.').last,
      'status': status.toString().split('.').last,
      'is_muted': isMuted,
      'is_speaking': isSpeaking,
      'has_raised_hand': hasRaisedHand,
      'joined_at': joinedAt.toIso8601String(),
      'last_spoke_at': lastSpokeAt?.toIso8601String(),
      'total_speak_time': totalSpeakTime,
      'audio_stats': audioStats,
      'permissions': permissions,
      'metadata': metadata,
    };
  }

  AudioParticipant copyWith({
    String? id,
    String? userId,
    String? username,
    String? avatarUrl,
    String? roomId,
    ParticipantRole? role,
    ParticipantStatus? status,
    bool? isMuted,
    bool? isSpeaking,
    bool? hasRaisedHand,
    DateTime? joinedAt,
    DateTime? lastSpokeAt,
    int? totalSpeakTime,
    Map<String, dynamic>? audioStats,
    List<String>? permissions,
    Map<String, dynamic>? metadata,
  }) {
    return AudioParticipant(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      username: username ?? this.username,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      roomId: roomId ?? this.roomId,
      role: role ?? this.role,
      status: status ?? this.status,
      isMuted: isMuted ?? this.isMuted,
      isSpeaking: isSpeaking ?? this.isSpeaking,
      hasRaisedHand: hasRaisedHand ?? this.hasRaisedHand,
      joinedAt: joinedAt ?? this.joinedAt,
      lastSpokeAt: lastSpokeAt ?? this.lastSpokeAt,
      totalSpeakTime: totalSpeakTime ?? this.totalSpeakTime,
      audioStats: audioStats ?? this.audioStats,
      permissions: permissions ?? this.permissions,
      metadata: metadata ?? this.metadata,
    );
  }

  bool get canSpeak => role == ParticipantRole.host || 
                       role == ParticipantRole.coHost || 
                       role == ParticipantRole.speaker ||
                       permissions.contains('speak');
  
  bool get canModerate => role == ParticipantRole.host || 
                         role == ParticipantRole.moderator ||
                         permissions.contains('moderate');
  
  bool get canInvite => role == ParticipantRole.host || 
                       role == ParticipantRole.coHost ||
                       permissions.contains('invite');
  
  bool get canMuteOthers => role == ParticipantRole.host || 
                           role == ParticipantRole.moderator ||
                           permissions.contains('mute_others');
  
  bool get isHost => role == ParticipantRole.host;
  bool get isCoHost => role == ParticipantRole.coHost;
  bool get isSpeaker => role == ParticipantRole.speaker;
  bool get isListener => role == ParticipantRole.listener;
  bool get isModerator => role == ParticipantRole.moderator;
  
  Duration get timeInRoom => DateTime.now().difference(joinedAt);
  Duration get timeSinceLastSpoke => lastSpokeAt != null ? 
      DateTime.now().difference(lastSpokeAt!) : Duration.zero;
} 