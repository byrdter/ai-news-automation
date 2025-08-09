// TypeScript types generated from database/models.py schema

export interface Database {
  public: {
    Tables: {
      news_sources: {
        Row: {
          id: string
          name: string
          url: string
          rss_feed_url: string | null
          tier: number
          category: string | null
          active: boolean
          fetch_interval: number
          max_articles_per_fetch: number
          last_fetched_at: string | null
          last_successful_fetch_at: string | null
          consecutive_failures: number
          total_articles_fetched: number
          metadata_json: any | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          url: string
          rss_feed_url?: string | null
          tier?: number
          category?: string | null
          active?: boolean
          fetch_interval?: number
          max_articles_per_fetch?: number
          last_fetched_at?: string | null
          last_successful_fetch_at?: string | null
          consecutive_failures?: number
          total_articles_fetched?: number
          metadata_json?: any | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          url?: string
          rss_feed_url?: string | null
          tier?: number
          category?: string | null
          active?: boolean
          fetch_interval?: number
          max_articles_per_fetch?: number
          last_fetched_at?: string | null
          last_successful_fetch_at?: string | null
          consecutive_failures?: number
          total_articles_fetched?: number
          metadata_json?: any | null
          created_at?: string
          updated_at?: string
        }
      }
      articles: {
        Row: {
          id: string
          title: string
          url: string
          content: string | null
          summary: string | null
          source_id: string
          published_at: string | null
          author: string | null
          word_count: number | null
          processed: boolean
          processing_stage: string | null
          processing_errors: any | null
          relevance_score: number
          sentiment_score: number
          quality_score: number
          urgency_score: number
          categories: string[] | null
          entities: any | null
          keywords: string[] | null
          topics: string[] | null
          title_embedding: number[] | null
          content_embedding: number[] | null
          view_count: number
          share_count: number
          external_engagement: any | null
          content_hash: string | null
          duplicate_of_id: string | null
          analysis_model: string | null
          analysis_cost_usd: number
          analysis_timestamp: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          title: string
          url: string
          content?: string | null
          summary?: string | null
          source_id: string
          published_at?: string | null
          author?: string | null
          word_count?: number | null
          processed?: boolean
          processing_stage?: string | null
          processing_errors?: any | null
          relevance_score?: number
          sentiment_score?: number
          quality_score?: number
          urgency_score?: number
          categories?: string[] | null
          entities?: any | null
          keywords?: string[] | null
          topics?: string[] | null
          title_embedding?: number[] | null
          content_embedding?: number[] | null
          view_count?: number
          share_count?: number
          external_engagement?: any | null
          content_hash?: string | null
          duplicate_of_id?: string | null
          analysis_model?: string | null
          analysis_cost_usd?: number
          analysis_timestamp?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          title?: string
          url?: string
          content?: string | null
          summary?: string | null
          source_id?: string
          published_at?: string | null
          author?: string | null
          word_count?: number | null
          processed?: boolean
          processing_stage?: string | null
          processing_errors?: any | null
          relevance_score?: number
          sentiment_score?: number
          quality_score?: number
          urgency_score?: number
          categories?: string[] | null
          entities?: any | null
          keywords?: string[] | null
          topics?: string[] | null
          title_embedding?: number[] | null
          content_embedding?: number[] | null
          view_count?: number
          share_count?: number
          external_engagement?: any | null
          content_hash?: string | null
          duplicate_of_id?: string | null
          analysis_model?: string | null
          analysis_cost_usd?: number
          analysis_timestamp?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      reports: {
        Row: {
          id: string
          report_type: string
          report_date: string
          title: string
          executive_summary: string | null
          key_highlights: any | null
          trend_analysis: string | null
          category_breakdown: any | null
          full_content: string | null
          generation_model: string | null
          generation_cost_usd: number
          generation_duration: number | null
          template_version: string | null
          status: string
          delivery_status: string | null
          delivery_attempts: number
          delivered_at: string | null
          article_count: number
          avg_relevance_score: number | null
          coverage_completeness: number | null
          recipients: string[] | null
          email_subject: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          report_type: string
          report_date: string
          title: string
          executive_summary?: string | null
          key_highlights?: any | null
          trend_analysis?: string | null
          category_breakdown?: any | null
          full_content?: string | null
          generation_model?: string | null
          generation_cost_usd?: number
          generation_duration?: number | null
          template_version?: string | null
          status?: string
          delivery_status?: string | null
          delivery_attempts?: number
          delivered_at?: string | null
          article_count?: number
          avg_relevance_score?: number | null
          coverage_completeness?: number | null
          recipients?: string[] | null
          email_subject?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          report_type?: string
          report_date?: string
          title?: string
          executive_summary?: string | null
          key_highlights?: any | null
          trend_analysis?: string | null
          category_breakdown?: any | null
          full_content?: string | null
          generation_model?: string | null
          generation_cost_usd?: number
          generation_duration?: number | null
          template_version?: string | null
          status?: string
          delivery_status?: string | null
          delivery_attempts?: number
          delivered_at?: string | null
          article_count?: number
          avg_relevance_score?: number | null
          coverage_completeness?: number | null
          recipients?: string[] | null
          email_subject?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      report_articles: {
        Row: {
          report_id: string
          article_id: string
          section: string | null
          importance_score: number
          summary_snippet: string | null
          position_in_section: number | null
        }
        Insert: {
          report_id: string
          article_id: string
          section?: string | null
          importance_score?: number
          summary_snippet?: string | null
          position_in_section?: number | null
        }
        Update: {
          report_id?: string
          article_id?: string
          section?: string | null
          importance_score?: number
          summary_snippet?: string | null
          position_in_section?: number | null
        }
      }
      alerts: {
        Row: {
          id: string
          title: string
          message: string
          alert_type: string | null
          urgency_level: string
          urgency_score: number | null
          article_id: string | null
          triggered_by_rules: any | null
          trigger_keywords: string[] | null
          trigger_entities: any | null
          delivery_status: string
          delivery_method: string | null
          delivery_attempts: number
          sent_at: string | null
          delivered_at: string | null
          is_throttled: boolean
          similar_alert_id: string | null
          alert_group: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          title: string
          message: string
          alert_type?: string | null
          urgency_level?: string
          urgency_score?: number | null
          article_id?: string | null
          triggered_by_rules?: any | null
          trigger_keywords?: string[] | null
          trigger_entities?: any | null
          delivery_status?: string
          delivery_method?: string | null
          delivery_attempts?: number
          sent_at?: string | null
          delivered_at?: string | null
          is_throttled?: boolean
          similar_alert_id?: string | null
          alert_group?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          title?: string
          message?: string
          alert_type?: string | null
          urgency_level?: string
          urgency_score?: number | null
          article_id?: string | null
          triggered_by_rules?: any | null
          trigger_keywords?: string[] | null
          trigger_entities?: any | null
          delivery_status?: string
          delivery_method?: string | null
          delivery_attempts?: number
          sent_at?: string | null
          delivered_at?: string | null
          is_throttled?: boolean
          similar_alert_id?: string | null
          alert_group?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      source_statistics: {
        Row: {
          id: string
          source_id: string
          date: string
          articles_fetched: number
          articles_processed: number
          articles_relevant: number
          articles_included_in_reports: number
          avg_relevance_score: number | null
          avg_quality_score: number | null
          avg_word_count: number | null
          fetch_duration: number | null
          processing_duration: number | null
          error_count: number
          error_types: any | null
          processing_cost_usd: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          source_id: string
          date: string
          articles_fetched?: number
          articles_processed?: number
          articles_relevant?: number
          articles_included_in_reports?: number
          avg_relevance_score?: number | null
          avg_quality_score?: number | null
          avg_word_count?: number | null
          fetch_duration?: number | null
          processing_duration?: number | null
          error_count?: number
          error_types?: any | null
          processing_cost_usd?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          source_id?: string
          date?: string
          articles_fetched?: number
          articles_processed?: number
          articles_relevant?: number
          articles_included_in_reports?: number
          avg_relevance_score?: number | null
          avg_quality_score?: number | null
          avg_word_count?: number | null
          fetch_duration?: number | null
          processing_duration?: number | null
          error_count?: number
          error_types?: any | null
          processing_cost_usd?: number
          created_at?: string
          updated_at?: string
        }
      }
      system_metrics: {
        Row: {
          id: string
          timestamp: string
          articles_processed_per_minute: number | null
          avg_processing_time: number | null
          pipeline_success_rate: number | null
          agent_response_times: any | null
          agent_success_rates: any | null
          active_agents: number | null
          llm_api_calls: number | null
          total_tokens_used: number | null
          tokens_by_model: any | null
          estimated_cost_usd: number
          daily_cost_usd: number | null
          monthly_cost_usd: number | null
          mcp_server_status: any | null
          database_connection_pool: any | null
          error_rate: number
          cpu_usage_percent: number | null
          memory_usage_mb: number | null
          disk_usage_mb: number | null
          workflow_completion_times: any | null
          workflow_success_rates: any | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          timestamp: string
          articles_processed_per_minute?: number | null
          avg_processing_time?: number | null
          pipeline_success_rate?: number | null
          agent_response_times?: any | null
          agent_success_rates?: any | null
          active_agents?: number | null
          llm_api_calls?: number | null
          total_tokens_used?: number | null
          tokens_by_model?: any | null
          estimated_cost_usd?: number
          daily_cost_usd?: number | null
          monthly_cost_usd?: number | null
          mcp_server_status?: any | null
          database_connection_pool?: any | null
          error_rate?: number
          cpu_usage_percent?: number | null
          memory_usage_mb?: number | null
          disk_usage_mb?: number | null
          workflow_completion_times?: any | null
          workflow_success_rates?: any | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          timestamp?: string
          articles_processed_per_minute?: number | null
          avg_processing_time?: number | null
          pipeline_success_rate?: number | null
          agent_response_times?: any | null
          agent_success_rates?: any | null
          active_agents?: number | null
          llm_api_calls?: number | null
          total_tokens_used?: number | null
          tokens_by_model?: any | null
          estimated_cost_usd?: number
          daily_cost_usd?: number | null
          monthly_cost_usd?: number | null
          mcp_server_status?: any | null
          database_connection_pool?: any | null
          error_rate?: number
          cpu_usage_percent?: number | null
          memory_usage_mb?: number | null
          disk_usage_mb?: number | null
          workflow_completion_times?: any | null
          workflow_success_rates?: any | null
          created_at?: string
          updated_at?: string
        }
      }
      cost_tracking: {
        Row: {
          id: string
          operation_type: string
          operation_id: string | null
          provider: string
          model_name: string
          api_endpoint: string | null
          input_tokens: number
          output_tokens: number
          total_tokens: number
          request_count: number
          input_cost_per_token: number | null
          output_cost_per_token: number | null
          base_cost: number
          total_cost_usd: number
          article_id: string | null
          report_id: string | null
          user_id: string | null
          session_id: string | null
          response_time_ms: number | null
          success: boolean
          error_message: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          operation_type: string
          operation_id?: string | null
          provider: string
          model_name: string
          api_endpoint?: string | null
          input_tokens?: number
          output_tokens?: number
          total_tokens?: number
          request_count?: number
          input_cost_per_token?: number | null
          output_cost_per_token?: number | null
          base_cost?: number
          total_cost_usd: number
          article_id?: string | null
          report_id?: string | null
          user_id?: string | null
          session_id?: string | null
          response_time_ms?: number | null
          success?: boolean
          error_message?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          operation_type?: string
          operation_id?: string | null
          provider?: string
          model_name?: string
          api_endpoint?: string | null
          input_tokens?: number
          output_tokens?: number
          total_tokens?: number
          request_count?: number
          input_cost_per_token?: number | null
          output_cost_per_token?: number | null
          base_cost?: number
          total_cost_usd?: number
          article_id?: string | null
          report_id?: string | null
          user_id?: string | null
          session_id?: string | null
          response_time_ms?: number | null
          success?: boolean
          error_message?: string | null
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      search_articles_by_similarity: {
        Args: {
          query_embedding: number[]
          similarity_threshold?: number
          max_results?: number
        }
        Returns: {
          id: string
          title: string
          content: string
          similarity: number
        }[]
      }
    }
    Enums: {
      [_ in never]: never
    }
  }
}

// Convenience types for common operations
export type Article = Database['public']['Tables']['articles']['Row']
export type NewArticle = Database['public']['Tables']['articles']['Insert']
export type ArticleUpdate = Database['public']['Tables']['articles']['Update']

export type Report = Database['public']['Tables']['reports']['Row']
export type NewReport = Database['public']['Tables']['reports']['Insert']
export type ReportUpdate = Database['public']['Tables']['reports']['Update']

export type NewsSource = Database['public']['Tables']['news_sources']['Row']
export type NewNewsSource = Database['public']['Tables']['news_sources']['Insert']
export type NewsSourceUpdate = Database['public']['Tables']['news_sources']['Update']

export type Alert = Database['public']['Tables']['alerts']['Row']
export type SystemMetrics = Database['public']['Tables']['system_metrics']['Row']
export type CostTracking = Database['public']['Tables']['cost_tracking']['Row']
export type SourceStatistics = Database['public']['Tables']['source_statistics']['Row']
export type ReportArticle = Database['public']['Tables']['report_articles']['Row']

// Extended types with relationships
export type ArticleWithSource = Article & {
  source: NewsSource
}

export type ReportWithArticles = Report & {
  report_articles: (ReportArticle & {
    article: Article
  })[]
}