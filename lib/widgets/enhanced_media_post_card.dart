import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/media_post.dart';
import '../models/mma_reddit_post.dart';

class EnhancedMediaPostCard extends StatelessWidget {
  final dynamic post; // MediaPost or MMARedditPost
  final VoidCallback? onTap;
  final bool showThumbnail;
  final bool compact;
  
  const EnhancedMediaPostCard({
    Key? key,
    required this.post,
    this.onTap,
    this.showThumbnail = true,
    this.compact = false,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    if (post is MediaPost) {
      return _buildMediaPostCard(context, post as MediaPost);
    } else if (post is MMARedditPost) {
      return _buildRedditPostCard(context, post as MMARedditPost);
    }
    
    return const SizedBox.shrink();
  }
  
  Widget _buildMediaPostCard(BuildContext context, MediaPost mediaPost) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A1A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _getPlatformColor(mediaPost.platform).withOpacity(0.3),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: InkWell(
        onTap: onTap ?? () => _launchUrl(mediaPost.url),
        borderRadius: BorderRadius.circular(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Thumbnail section
            if (showThumbnail)
              Container(
                height: compact ? 140 : 200,
                width: double.infinity,
                decoration: BoxDecoration(
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                  gradient: _getThemedGradient(mediaPost.platform, mediaPost.contentType),
                ),
                child: Stack(
                  children: [
                    // Themed background pattern
                    Positioned.fill(
                      child: CustomPaint(
                        painter: ThemedBackgroundPainter(
                          platform: mediaPost.platform,
                          contentType: mediaPost.contentType,
                        ),
                      ),
                    ),
                    
                    // Platform badge
                    Positioned(
                      top: 12,
                      left: 12,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: _getPlatformColor(mediaPost.platform).withOpacity(0.9),
                          borderRadius: BorderRadius.circular(20),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.3),
                              blurRadius: 4,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              mediaPost.platformIcon,
                              style: const TextStyle(fontSize: 14),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              mediaPost.platform.toUpperCase(),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    
                    // Content type badge
                    Positioned(
                      top: 12,
                      right: 12,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: mediaPost.contentTypeColor.withOpacity(0.9),
                          borderRadius: BorderRadius.circular(12),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.3),
                              blurRadius: 4,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              mediaPost.contentTypeIcon,
                              style: const TextStyle(fontSize: 12),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              mediaPost.contentType.toUpperCase(),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 9,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    
                    // Duration overlay for videos
                    if (mediaPost.durationSeconds != null && mediaPost.durationSeconds! > 0)
                      Positioned(
                        bottom: 12,
                        right: 12,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.8),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            mediaPost.formattedDuration,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    
                    // Play button for videos
                    if (mediaPost.platform == 'youtube')
                      Center(
                        child: Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: Colors.red.withOpacity(0.9),
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.3),
                                blurRadius: 8,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.play_arrow,
                            color: Colors.white,
                            size: 24,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            
            // Content section
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title
                  Text(
                    mediaPost.title,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      height: 1.3,
                    ),
                    maxLines: compact ? 2 : 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                  
                  const SizedBox(height: 12),
                  
                  // Author and verification
                  Row(
                    children: [
                      // Author avatar placeholder
                      Container(
                        width: 24,
                        height: 24,
                        decoration: BoxDecoration(
                          color: _getPlatformColor(mediaPost.platform).withOpacity(0.2),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.person,
                          size: 14,
                          color: _getPlatformColor(mediaPost.platform),
                        ),
                      ),
                      
                      const SizedBox(width: 8),
                      
                      // Author name
                      Expanded(
                        child: Text(
                          mediaPost.authorName,
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      
                      // Verified badge
                      if (mediaPost.authorVerified == true)
                        Container(
                          margin: const EdgeInsets.only(left: 4),
                          child: const Icon(
                            Icons.verified,
                            size: 16,
                            color: Colors.blue,
                          ),
                        ),
                    ],
                  ),
                  
                  const SizedBox(height: 12),
                  
                  // Engagement metrics
                  Row(
                    children: [
                      // View count
                      if (mediaPost.viewCount > 0) ...[
                        Icon(
                          Icons.visibility,
                          size: 16,
                          color: Colors.grey.withOpacity(0.7),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          mediaPost.formattedViewCount,
                          style: TextStyle(
                            color: Colors.grey.withOpacity(0.7),
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(width: 16),
                      ],
                      
                      // Like count
                      if (mediaPost.likeCount > 0) ...[
                        Icon(
                          Icons.favorite,
                          size: 16,
                          color: Colors.grey.withOpacity(0.7),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          mediaPost.formattedLikeCount,
                          style: TextStyle(
                            color: Colors.grey.withOpacity(0.7),
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(width: 16),
                      ],
                      
                      // Time ago
                      Icon(
                        Icons.access_time,
                        size: 16,
                        color: Colors.grey.withOpacity(0.7),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        mediaPost.timeAgo,
                        style: TextStyle(
                          color: Colors.grey.withOpacity(0.7),
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      
                      const Spacer(),
                      
                      // Relevance score indicator
                      if (mediaPost.relevanceScore > 0)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: _getRelevanceColor(mediaPost.relevanceScore).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.trending_up,
                                size: 12,
                                color: _getRelevanceColor(mediaPost.relevanceScore),
                              ),
                              const SizedBox(width: 2),
                              Text(
                                '${mediaPost.relevanceScore}',
                                style: TextStyle(
                                  color: _getRelevanceColor(mediaPost.relevanceScore),
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildRedditPostCard(BuildContext context, MMARedditPost redditPost) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A1A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.orange.withOpacity(0.3),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: InkWell(
        onTap: onTap ?? () => _launchUrl(redditPost.redditUrl),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Reddit header
              Row(
                children: [
                  // Reddit icon
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: Colors.orange.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.reddit,
                      color: Colors.orange,
                      size: 20,
                    ),
                  ),
                  
                  const SizedBox(width: 12),
                  
                  // Subreddit and author
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'r/${redditPost.subreddit}',
                          style: const TextStyle(
                            color: Colors.orange,
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'by ${redditPost.redditAuthor}',
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  // Quality indicators
                  if (redditPost.isHighQuality || redditPost.isRecent)
                    Row(
                      children: [
                        if (redditPost.isHighQuality)
                          Container(
                            margin: const EdgeInsets.only(right: 4),
                            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.green.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Icon(
                              Icons.star,
                              size: 10,
                              color: Colors.green,
                            ),
                          ),
                        if (redditPost.isRecent)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.blue.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Icon(
                              Icons.new_releases,
                              size: 10,
                              color: Colors.blue,
                            ),
                          ),
                      ],
                    ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Title
              Text(
                redditPost.title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  height: 1.3,
                ),
                maxLines: compact ? 2 : 3,
                overflow: TextOverflow.ellipsis,
              ),
              
              const SizedBox(height: 12),
              
              // Engagement metrics
              Row(
                children: [
                  // Score
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.grey.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.arrow_upward,
                          size: 14,
                          color: Colors.green,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          redditPost.redditScore.toString(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(width: 12),
                  
                  // Comments
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.grey.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.chat_bubble_outline,
                          size: 14,
                          color: Colors.blue,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          redditPost.redditComments.toString(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const Spacer(),
                  
                  // Time ago
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.grey.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.access_time,
                          size: 12,
                          color: Colors.grey,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          redditPost.timeAgo,
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 10,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Color _getPlatformColor(String platform) {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return Colors.red;
      case 'twitter':
        return Colors.blue;
      case 'tiktok':
        return Colors.black;
      case 'reddit':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }
  
  LinearGradient _getThemedGradient(String platform, String contentType) {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFFF0000), Color(0xFFCC0000), Color(0xFF990000)],
        );
      case 'twitter':
        return const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1DA1F2), Color(0xFF0D8BD9), Color(0xFF0A6BC7)],
        );
      case 'tiktok':
        return const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF000000), Color(0xFF1A1A1A), Color(0xFF2D2D2D)],
        );
      case 'reddit':
        return const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFFF4500), Color(0xFFE63900), Color(0xFFCC3300)],
        );
      default:
        return const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF666666), Color(0xFF444444), Color(0xFF222222)],
        );
    }
  }
  
  Color _getRelevanceColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    if (score >= 40) return Colors.yellow.shade700;
    return Colors.grey;
  }
  
  Future<void> _launchUrl(String url) async {
    try {
      final uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    } catch (e) {
      print('Error launching URL: $e');
    }
  }
}

class ThemedBackgroundPainter extends CustomPainter {
  final String platform;
  final String contentType;
  
  ThemedBackgroundPainter({
    required this.platform,
    required this.contentType,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;
    
    // Draw themed patterns based on platform and content type
    switch (platform.toLowerCase()) {
      case 'youtube':
        _drawYouTubePattern(canvas, size, paint);
        break;
      case 'twitter':
        _drawTwitterPattern(canvas, size, paint);
        break;
      case 'tiktok':
        _drawTikTokPattern(canvas, size, paint);
        break;
      case 'reddit':
        _drawRedditPattern(canvas, size, paint);
        break;
      default:
        _drawDefaultPattern(canvas, size, paint);
    }
  }
  
  void _drawYouTubePattern(Canvas canvas, Size size, Paint paint) {
    // Draw play button icon pattern
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width * 0.15;
    
    canvas.drawCircle(center, radius, paint);
    canvas.drawCircle(center, radius - 20, paint);
    
    // Draw small play triangles
    for (int i = 0; i < 3; i++) {
      final x = size.width * (0.2 + i * 0.3);
      final y = size.height * 0.3;
      final trianglePath = Path()
        ..moveTo(x, y)
        ..lineTo(x + 15, y + 10)
        ..lineTo(x, y + 20)
        ..close();
      canvas.drawPath(trianglePath, paint);
    }
  }
  
  void _drawTwitterPattern(Canvas canvas, Size size, Paint paint) {
    // Draw bird-like pattern
    final center = Offset(size.width / 2, size.height / 2);
    
    // Draw curved lines representing wings
    final wingPath = Path()
      ..moveTo(center.dx - 30, center.dy)
      ..quadraticBezierTo(center.dx - 15, center.dy - 20, center.dx, center.dy - 10)
      ..quadraticBezierTo(center.dx + 15, center.dy - 20, center.dx + 30, center.dy);
    canvas.drawPath(wingPath, paint);
    
    // Draw small circles for eyes
    canvas.drawCircle(Offset(center.dx - 10, center.dy - 5), 3, paint);
    canvas.drawCircle(Offset(center.dx + 10, center.dy - 5), 3, paint);
  }
  
  void _drawTikTokPattern(Canvas canvas, Size size, Paint paint) {
    // Draw musical note pattern
    final center = Offset(size.width / 2, size.height / 2);
    
    // Draw note stems
    for (int i = 0; i < 3; i++) {
      final x = center.dx - 20 + i * 20;
      final y = center.dy - 20;
      canvas.drawLine(Offset(x, y), Offset(x, y + 30), paint);
      
      // Draw note heads
      canvas.drawCircle(Offset(x, y + 30), 5, paint);
    }
  }
  
  void _drawRedditPattern(Canvas canvas, Size size, Paint paint) {
    // Draw upvote arrow pattern
    final center = Offset(size.width / 2, size.height / 2);
    
    for (int i = 0; i < 3; i++) {
      final x = center.dx - 20 + i * 20;
      final y = center.dy;
      
      final arrowPath = Path()
        ..moveTo(x, y + 10)
        ..lineTo(x + 5, y)
        ..lineTo(x + 10, y + 10)
        ..moveTo(x + 2, y + 10)
        ..lineTo(x + 8, y + 10)
        ..lineTo(x + 8, y + 20)
        ..lineTo(x + 2, y + 20)
        ..close();
      canvas.drawPath(arrowPath, paint);
    }
  }
  
  void _drawDefaultPattern(Canvas canvas, Size size, Paint paint) {
    // Draw simple grid pattern
    final spacing = 30.0;
    
    for (double x = 0; x < size.width; x += spacing) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    
    for (double y = 0; y < size.height; y += spacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }
  
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
