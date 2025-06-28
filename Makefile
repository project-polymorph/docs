.PHONY: build clean analyze

build: analyze
	# make docs/文档/编年录/新闻报道
	# make docs/文档/编年录/学术研究与调查报告
	# make docs/文档/编年录/政策法规
	# make docs/文档/编年录/综合索引
	python scripts/generate_homepage.py

# Add new analyze target and its dependencies
analyze: download process-indices merge-index

download:
	export OPENAI_TEMPERATURE=0.7 && \
	python .github/scripts/toc/independence_info.py && \
	mkdir -p results/ && cp independence_repo.json results/independence_repo.json && \
	python scripts/analysis/download.py
	mkdir -p docs/数据统计
	@echo "Download complete."

process-indices:
	@for index_file in index/*/search_index.yml; do \
		name=$$(basename $$(dirname "$$index_file")); \
		echo "Processing $$name..."; \
		python .github/scripts/file/analysis_search_index.py \
			-i "$$index_file" \
			-o "results/$${name}_analysis.yml"; \
		python scripts/analysis/basic_report.py \
			-i "results/$${name}_analysis.yml" \
			-o "docs/数据统计/$${name}.md"; \
	done
	@echo "Analysis complete. Results saved in results/"

merge-index:
	python scripts/analysis/merge_index.py
	@echo "Merge complete. Results saved in index/combined_index.yml"

docs/文档/编年录/新闻报道:
	mkdir -p docs/文档/编年录/新闻报道
	cd docs/文档/编年录 && python ../../../scripts/generate_index.py --config news_query.json --state .news_index_state.json

docs/文档/编年录/学术研究与调查报告:
	mkdir -p docs/文档/编年录/学术研究与调查报告
	cd docs/文档/编年录 && python ../../../scripts/generate_index.py --config paper_query.json --state .paper_index_state.json	

docs/文档/编年录/政策法规:
	cp -R templates/政策法规 docs/文档/编年录/政策法规
	cd docs/文档/编年录 && python ../../../scripts/generate_index.py --config policy_query.json --state .policy_index_state.json

docs/文档/编年录/综合索引:
	mkdir -p docs/文档/编年录/综合索引
	cd docs/文档/编年录 && python ../../../scripts/generate_index.py --config total_query.json --state .total_index_state.json

clean:
	rm -rf docs/文档/编年录/新闻报道
	rm -rf docs/文档/编年录/学术研究与调查报告
	rm -rf docs/文档/编年录/政策法规
	rm -f docs/文档/编年录/.news_index_state.json
	rm -f docs/文档/编年录/.paper_index_state.json
	rm -f docs/文档/编年录/.policy_index_state.json
	rm -f docs/文档/编年录/.total_index_state.json
	rm -rf results/*
	rm -rf docs/数据统计/*

