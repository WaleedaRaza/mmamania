enum AudioSessionStatus {
  initializing,
  connecting,
  connected,
  reconnecting,
  disconnected,
  error,
}

enum AudioQuality {
  low,
  medium,
  high,
  ultra,
}

class AudioSession {
  final String id;
  final String roomId;
  final String userId;
  final AudioSessionStatus status;
  final AudioQuality quality;
  final bool isMuted;
  final bool isDeafened;
  final double volume;
  final double inputVolume;
  final double outputVolume;
  final bool echoCancellation;
  final bool noiseSuppression;
  final bool autoGainControl;
  final DateTime connectedAt;
  final DateTime? lastActivityAt;
  final Map<String, dynamic>? connectionStats;
  final Map<String, dynamic>? audioStats;
  final List<String> connectedPeers;
  final Map<String, dynamic>? metadata;

  AudioSession({
    required this.id,
    required this.roomId,
    required this.userId,
    this.status = AudioSessionStatus.initializing,
    this.quality = AudioQuality.medium,
    this.isMuted = false,
    this.isDeafened = false,
    this.volume = 1.0,
    this.inputVolume = 1.0,
    this.outputVolume = 1.0,
    this.echoCancellation = true,
    this.noiseSuppression = true,
    this.autoGainControl = true,
    required this.connectedAt,
    this.lastActivityAt,
    this.connectionStats,
    this.audioStats,
    this.connectedPeers = const [],
    this.metadata,
  });

  factory AudioSession.fromJson(Map<String, dynamic> json) {
    return AudioSession(
      id: json['id'],
      roomId: json['room_id'],
      userId: json['user_id'],
      status: AudioSessionStatus.values.firstWhere(
        (e) => e.toString() == 'AudioSessionStatus.${json['status']}',
        orElse: () => AudioSessionStatus.initializing,
      ),
      quality: AudioQuality.values.firstWhere(
        (e) => e.toString() == 'AudioQuality.${json['quality']}',
        orElse: () => AudioQuality.medium,
      ),
      isMuted: json['is_muted'] ?? false,
      isDeafened: json['is_deafened'] ?? false,
      volume: (json['volume'] ?? 1.0).toDouble(),
      inputVolume: (json['input_volume'] ?? 1.0).toDouble(),
      outputVolume: (json['output_volume'] ?? 1.0).toDouble(),
      echoCancellation: json['echo_cancellation'] ?? true,
      noiseSuppression: json['noise_suppression'] ?? true,
      autoGainControl: json['auto_gain_control'] ?? true,
      connectedAt: DateTime.parse(json['connected_at']),
      lastActivityAt: json['last_activity_at'] != null ? DateTime.parse(json['last_activity_at']) : null,
      connectionStats: json['connection_stats'],
      audioStats: json['audio_stats'],
      connectedPeers: (json['connected_peers'] as List<dynamic>?)?.cast<String>() ?? [],
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'room_id': roomId,
      'user_id': userId,
      'status': status.toString().split('.').last,
      'quality': quality.toString().split('.').last,
      'is_muted': isMuted,
      'is_deafened': isDeafened,
      'volume': volume,
      'input_volume': inputVolume,
      'output_volume': outputVolume,
      'echo_cancellation': echoCancellation,
      'noise_suppression': noiseSuppression,
      'auto_gain_control': autoGainControl,
      'connected_at': connectedAt.toIso8601String(),
      'last_activity_at': lastActivityAt?.toIso8601String(),
      'connection_stats': connectionStats,
      'audio_stats': audioStats,
      'connected_peers': connectedPeers,
      'metadata': metadata,
    };
  }

  AudioSession copyWith({
    String? id,
    String? roomId,
    String? userId,
    AudioSessionStatus? status,
    AudioQuality? quality,
    bool? isMuted,
    bool? isDeafened,
    double? volume,
    double? inputVolume,
    double? outputVolume,
    bool? echoCancellation,
    bool? noiseSuppression,
    bool? autoGainControl,
    DateTime? connectedAt,
    DateTime? lastActivityAt,
    Map<String, dynamic>? connectionStats,
    Map<String, dynamic>? audioStats,
    List<String>? connectedPeers,
    Map<String, dynamic>? metadata,
  }) {
    return AudioSession(
      id: id ?? this.id,
      roomId: roomId ?? this.roomId,
      userId: userId ?? this.userId,
      status: status ?? this.status,
      quality: quality ?? this.quality,
      isMuted: isMuted ?? this.isMuted,
      isDeafened: isDeafened ?? this.isDeafened,
      volume: volume ?? this.volume,
      inputVolume: inputVolume ?? this.inputVolume,
      outputVolume: outputVolume ?? this.outputVolume,
      echoCancellation: echoCancellation ?? this.echoCancellation,
      noiseSuppression: noiseSuppression ?? this.noiseSuppression,
      autoGainControl: autoGainControl ?? this.autoGainControl,
      connectedAt: connectedAt ?? this.connectedAt,
      lastActivityAt: lastActivityAt ?? this.lastActivityAt,
      connectionStats: connectionStats ?? this.connectionStats,
      audioStats: audioStats ?? this.audioStats,
      connectedPeers: connectedPeers ?? this.connectedPeers,
      metadata: metadata ?? this.metadata,
    );
  }

  bool get isConnected => status == AudioSessionStatus.connected;
  bool get isConnecting => status == AudioSessionStatus.connecting || status == AudioSessionStatus.reconnecting;
  bool get hasError => status == AudioSessionStatus.error;
  bool get isDisconnected => status == AudioSessionStatus.disconnected;
  
  Duration get connectionDuration => DateTime.now().difference(connectedAt);
  Duration get timeSinceLastActivity => lastActivityAt != null ? 
      DateTime.now().difference(lastActivityAt!) : Duration.zero;
  
  bool get canHear => !isDeafened && isConnected;
  bool get canSpeak => !isMuted && isConnected;
  
  // Audio quality settings
  int get sampleRate {
    switch (quality) {
      case AudioQuality.low:
        return 8000;
      case AudioQuality.medium:
        return 16000;
      case AudioQuality.high:
        return 32000;
      case AudioQuality.ultra:
        return 48000;
    }
  }
  
  int get bitrate {
    switch (quality) {
      case AudioQuality.low:
        return 32;
      case AudioQuality.medium:
        return 64;
      case AudioQuality.high:
        return 128;
      case AudioQuality.ultra:
        return 256;
    }
  }
} 