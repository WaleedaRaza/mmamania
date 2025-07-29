import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/mma_feed_provider.dart';
import '../models/mma_post.dart';
import '../models/mma_reddit_post.dart';
import 'package:url_launcher/url_launcher.dart';

class MMAFeedScreen extends StatefulWidget {
  const MMAFeedScreen({super.key});

  @override
  State<MMAFeedScreen> createState() => _MMAFeedScreenState();
}

class _MMAFeedScreenState extends State<MMAFeedScreen> {
  bool _hasInitialized = false;

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => MMAFeedProvider(),
      child: Builder(
        builder: (context) {
          // Fetch posts only once after first build
          if (!_hasInitialized) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                Provider.of<MMAFeedProvider>(context, listen: false).fetchPosts(context);
                setState(() {
                  _hasInitialized = true;
                });
              }
            });
          }
          
          return Consumer<MMAFeedProvider>(
            builder: (context, provider, child) {
              return Scaffold(
                appBar: AppBar(
                  title: const Text('MMA Feed'),
                  actions: [
                    IconButton(
                      icon: const Icon(Icons.refresh),
                      onPressed: () => provider.fetchPosts(context),
                    ),
                  ],
                ),
                body: provider.isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : provider.errorMessage != null
                        ? Center(child: Text(provider.errorMessage!))
                        : ListView.builder(
                            itemCount: provider.posts.length,
                            itemBuilder: (context, index) {
                              final post = provider.posts[index];
                              if (post is MMARedditPost) {
                                return _buildRedditPostCard(post);
                              } else {
                                return _buildGenericPostCard(post);
                              }
                            },
                          ),
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildRedditPostCard(MMARedditPost post) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ListTile(
        leading: post.redditThumbnail != null
            ? Image.network(post.redditThumbnail!, width: 48, height: 48, fit: BoxFit.cover)
            : const Icon(Icons.reddit, color: Colors.orange, size: 40),
        title: Text(post.title, maxLines: 2, overflow: TextOverflow.ellipsis),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('r/${post.subreddit} • u/${post.redditAuthor}'),
            Text('${post.redditScore} upvotes • ${post.redditComments} comments'),
            Text(post.categorizePost().toString().split('.').last),
          ],
        ),
        onTap: () => _showRedditPostDetail(context, post),
      ),
    );
  }

  void _showRedditPostDetail(BuildContext context, MMARedditPost post) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(post.title),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (post.redditThumbnail != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Image.network(post.redditThumbnail!, height: 180, fit: BoxFit.cover),
                  ),
                Text('Subreddit: r/${post.subreddit}'),
                Text('Author: u/${post.redditAuthor}'),
                Text('Upvotes: ${post.redditScore}'),
                Text('Comments: ${post.redditComments}'),
                const SizedBox(height: 12),
                Text(post.content.isNotEmpty ? post.content : '[No text content]', style: const TextStyle(fontSize: 15)),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () async {
                final url = post.redditUrl;
                if (await canLaunchUrl(Uri.parse(url))) {
                  await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Could not open Reddit link')),
                  );
                }
              },
              child: const Text('Open in Reddit'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildGenericPostCard(MMAPost post) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ListTile(
        title: Text(post.title),
        subtitle: Text(post.content, maxLines: 2, overflow: TextOverflow.ellipsis),
      ),
    );
  }
}